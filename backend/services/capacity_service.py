# backend/services/capacity_service.py
"""
Capacity Management Service
Handles segment-based capacity tracking, validation, and booking allocation
"""
import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from backend.models import (
    TrainSchedule,
    TrainScheduleByStation,
    ScheduleCapacity,
    SegmentCapacity,
    DefaultScheduleCapacity,
    OperationalTrain,
    TrainModel,
    AllocationStatus,
    TrainClass
)
from backend.utils.calendar_service import is_poya_day, is_holiday

logger = logging.getLogger(__name__)


class CapacityService:
    """Service for managing train capacity and bookings"""

    @staticmethod
    def schedule_operates_on_date(
        schedule: TrainSchedule,
        check_date: date
    ) -> bool:
        """
        Check if a schedule operates on a given date

        Args:
            schedule: TrainSchedule object
            check_date: Date to check

        Returns:
            True if schedule operates on this date, False otherwise
        """
        # Get day of week (0=Monday, 6=Sunday)
        day_of_week = check_date.weekday()

        # Check if date is Poya day or holiday
        is_poya = is_poya_day(check_date)
        is_holiday_date = is_holiday(check_date)

        # Check day of week flags
        day_flags = [
            schedule.monday,    # 0
            schedule.tuesday,   # 1
            schedule.wednesday, # 2
            schedule.thursday,  # 3
            schedule.friday,    # 4
            schedule.saturday,  # 5
            schedule.sunday     # 6
        ]

        # Schedule operates if:
        # 1. Day of week matches AND not a Poya/holiday (normal operation)
        # 2. OR it's a Poya day and schedule.poya_day is True
        # 3. OR it's a holiday and schedule.holiday is True

        operates_on_day = day_flags[day_of_week]
        operates_on_poya = is_poya and schedule.poya_day
        operates_on_holiday = is_holiday_date and schedule.holiday

        operates = operates_on_day or operates_on_poya or operates_on_holiday

        logger.debug(
            f"Schedule {schedule.train_schedule_id} on {check_date}: "
            f"day={day_of_week}, poya={is_poya}, holiday={is_holiday_date}, "
            f"operates={operates}"
        )

        return operates

    @staticmethod
    def get_default_capacity(
        db: Session,
        train_schedule_id: str
    ) -> Optional[DefaultScheduleCapacity]:
        """
        Get default capacity configuration for a schedule

        Args:
            db: Database session
            train_schedule_id: Schedule ID

        Returns:
            DefaultScheduleCapacity object or None
        """
        return db.query(DefaultScheduleCapacity).filter(
            DefaultScheduleCapacity.train_schedule_id == train_schedule_id
        ).first()

    @staticmethod
    def calculate_class_capacity(
        compartments: int,
        seating_per_compartment: int,
        standing_per_compartment: int
    ) -> int:
        """
        Calculate total capacity for a class

        Args:
            compartments: Number of compartments
            seating_per_compartment: Seating passengers per compartment
            standing_per_compartment: Standing passengers per compartment

        Returns:
            Total capacity
        """
        return compartments * (seating_per_compartment + standing_per_compartment)

    @staticmethod
    def initialize_schedule_capacity(
        db: Session,
        schedule: TrainSchedule,
        schedule_date: date
    ) -> Optional[ScheduleCapacity]:
        """
        Initialize provisional capacity for a schedule on a specific date

        Args:
            db: Database session
            schedule: TrainSchedule object
            schedule_date: Date for the schedule

        Returns:
            Created ScheduleCapacity object or None if schedule doesn't operate
        """
        # Check if schedule operates on this date
        if not CapacityService.schedule_operates_on_date(schedule, schedule_date):
            logger.info(
                f"Schedule {schedule.train_schedule_id} does not operate on {schedule_date}"
            )
            return None

        # Get default capacity configuration
        default_capacity = CapacityService.get_default_capacity(
            db, schedule.train_schedule_id
        )

        if not default_capacity:
            logger.error(
                f"No default capacity configuration found for schedule {schedule.train_schedule_id}"
            )
            return None

        # Calculate planned capacities
        planned_first = CapacityService.calculate_class_capacity(
            default_capacity.first_class_compartments,
            default_capacity.seating_passengers_per_first_class,
            default_capacity.standing_passengers_per_first_class
        )
        planned_second = CapacityService.calculate_class_capacity(
            default_capacity.second_class_compartments,
            default_capacity.seating_passengers_per_second_class,
            default_capacity.standing_passengers_per_second_class
        )
        planned_third = CapacityService.calculate_class_capacity(
            default_capacity.third_class_compartments,
            default_capacity.seating_passengers_per_third_class,
            default_capacity.standing_passengers_per_third_class
        )

        # Create schedule capacity record
        schedule_capacity = ScheduleCapacity(
            schedule_id=schedule.train_schedule_id,
            schedule_date=schedule_date,
            allocation_status=AllocationStatus.Provisional,

            # Planned compartments
            planned_first_class_compartments=default_capacity.first_class_compartments,
            planned_second_class_compartments=default_capacity.second_class_compartments,
            planned_third_class_compartments=default_capacity.third_class_compartments,

            # Planned capacity
            planned_first_class_seats=planned_first,
            planned_second_class_seats=planned_second,
            planned_third_class_seats=planned_third
        )

        db.add(schedule_capacity)
        db.flush()  # Get the ID

        # Initialize segment capacities
        CapacityService._initialize_segment_capacities(
            db,
            schedule_capacity,
            schedule,
            planned_first,
            planned_second,
            planned_third
        )

        db.commit()

        logger.info(
            f"Initialized provisional capacity for {schedule.train_schedule_id} "
            f"on {schedule_date} (First: {planned_first}, Second: {planned_second}, Third: {planned_third})"
        )

        return schedule_capacity

    @staticmethod
    def _initialize_segment_capacities(
        db: Session,
        schedule_capacity: ScheduleCapacity,
        schedule: TrainSchedule,
        max_first: int,
        max_second: int,
        max_third: int
    ):
        """
        Initialize segment capacity records for a schedule

        Args:
            db: Database session
            schedule_capacity: ScheduleCapacity object
            schedule: TrainSchedule object
            max_first/second/third: Maximum capacity per class
        """
        # Get all station-to-station segments for this schedule
        segments = db.query(TrainScheduleByStation).filter(
            TrainScheduleByStation.train_schedule_id == schedule.train_schedule_id
        ).order_by(TrainScheduleByStation.origin_departure).all()

        if not segments:
            logger.warning(
                f"No segments found for schedule {schedule.train_schedule_id}"
            )
            return

        # Create segment capacity records
        for idx, segment in enumerate(segments, start=1):
            segment_capacity = SegmentCapacity(
                schedule_capacity_id=schedule_capacity.id,
                schedule_id=schedule.train_schedule_id,
                schedule_date=schedule_capacity.schedule_date,
                segment_order=idx,
                origin_station_id=segment.origin_station_id,
                origin_station=segment.origin_station,
                destination_station_id=segment.destination_station_id,
                destination_station=segment.destination_station,
                max_first_class=max_first,
                max_second_class=max_second,
                max_third_class=max_third,
                max_total=max_first + max_second + max_third
            )
            db.add(segment_capacity)

        logger.info(
            f"Initialized {len(segments)} segment capacity records for "
            f"{schedule.train_schedule_id} on {schedule_capacity.schedule_date}"
        )

    @staticmethod
    def get_or_create_schedule_capacity(
        db: Session,
        schedule_id: str,
        schedule_date: date
    ) -> Optional[ScheduleCapacity]:
        """
        Get existing or create new schedule capacity record

        Args:
            db: Database session
            schedule_id: Train schedule ID
            schedule_date: Date for the schedule

        Returns:
            ScheduleCapacity object or None
        """
        # Check if already exists
        schedule_capacity = db.query(ScheduleCapacity).filter(
            and_(
                ScheduleCapacity.schedule_id == schedule_id,
                ScheduleCapacity.schedule_date == schedule_date
            )
        ).first()

        if schedule_capacity:
            return schedule_capacity

        # Create new
        schedule = db.query(TrainSchedule).filter(
            TrainSchedule.train_schedule_id == schedule_id
        ).first()

        if not schedule:
            logger.error(f"Schedule {schedule_id} not found")
            return None

        return CapacityService.initialize_schedule_capacity(db, schedule, schedule_date)

    @staticmethod
    def find_overlapping_segments(
        db: Session,
        schedule_capacity_id: int,
        origin_station_id: str,
        destination_station_id: str
    ) -> List[SegmentCapacity]:
        """
        Find all segments that overlap with a booking from origin to destination
        
        The segments are ordered by origin_departure time to ensure we get the correct
        sequential segments from origin to destination station.

        Example: Booking from B to E on route A-B-C-D-E-F
        Returns segments: [B-C, C-D, D-E]

        Args:
            db: Database session
            schedule_capacity_id: Schedule capacity ID
            origin_station_id: Booking origin station
            destination_station_id: Booking destination station

        Returns:
            List of SegmentCapacity objects that overlap with the booking
        """
        # Get the schedule_id from the schedule_capacity to query the original schedule segments
        schedule_capacity = db.query(ScheduleCapacity).filter(
            ScheduleCapacity.id == schedule_capacity_id
        ).first()
        
        if not schedule_capacity:
            logger.error(f"Schedule capacity {schedule_capacity_id} not found")
            return []
        
        # Get the schedule segments ordered by departure time from TrainScheduleByStation
        schedule_segments = db.query(TrainScheduleByStation).filter(
            TrainScheduleByStation.train_schedule_id == schedule_capacity.schedule_id
        ).order_by(TrainScheduleByStation.origin_departure).all()
        
        if not schedule_segments:
            logger.warning(f"No schedule segments found for schedule {schedule_capacity.schedule_id}")
            return []
        
        # Get all capacity segments for this schedule capacity
        all_segments = db.query(SegmentCapacity).filter(
            SegmentCapacity.schedule_capacity_id == schedule_capacity_id
        ).all()
        
        # Create a lookup map for capacity segments by (origin_id, destination_id)
        segment_map = {
            (seg.origin_station_id, seg.destination_station_id): seg 
            for seg in all_segments
        }
        
        # Create a lookup map for capacity segments by (origin_id, destination_id)
        segment_map = {
            (seg.origin_station_id, seg.destination_station_id): seg 
            for seg in all_segments
        }

        # Now walk through schedule segments in departure order and collect overlapping ones
        overlapping = []
        collecting = False
        
        for schedule_seg in schedule_segments:
            # Start collecting when we find the origin station as the segment origin
            if not collecting:
                if schedule_seg.origin_station_id == origin_station_id:
                    collecting = True
            
            # If we're collecting, add the corresponding capacity segment
            if collecting:
                # Look up the capacity segment for this route segment
                capacity_seg = segment_map.get(
                    (schedule_seg.origin_station_id, schedule_seg.destination_station_id)
                )
                
                if capacity_seg:
                    overlapping.append(capacity_seg)
                else:
                    logger.warning(
                        f"Capacity segment not found for {schedule_seg.origin_station_id} → "
                        f"{schedule_seg.destination_station_id}"
                    )
                
                # Stop when we reach the destination as the segment destination
                if schedule_seg.destination_station_id == destination_station_id:
                    break

        if not overlapping:
            logger.warning(
                f"No segments found for {origin_station_id} → {destination_station_id}. "
                f"Available segments: {[(seg.origin_station_id, seg.destination_station_id) for seg in schedule_segments]}"
            )
        elif overlapping and overlapping[-1].destination_station_id != destination_station_id:
            logger.error(
                f"Path incomplete for {origin_station_id} → {destination_station_id}. "
                f"Last segment ends at: {overlapping[-1].destination_station_id}, "
                f"Expected: {destination_station_id}, "
                f"Collected {len(overlapping)} segments"
            )

        logger.debug(
            f"Found {len(overlapping)} overlapping segments for booking "
            f"{origin_station_id} → {destination_station_id}"
        )

        return overlapping

    @staticmethod
    def can_book_ticket(
        db: Session,
        schedule_id: str,
        schedule_date: date,
        origin_station_id: str,
        destination_station_id: str,
        train_class: TrainClass,
        num_passengers: int = 1
    ) -> Tuple[bool, Optional[str], Optional[SegmentCapacity]]:
        """
        Check if a ticket can be booked based on segment capacity

        Args:
            db: Database session
            schedule_id: Train schedule ID
            schedule_date: Travel date
            origin_station_id: Origin station
            destination_station_id: Destination station
            train_class: Train class (First/Second/Third)
            num_passengers: Number of passengers (default 1)

        Returns:
            Tuple of (can_book: bool, reason: str, bottleneck_segment: SegmentCapacity)
        """
        # Get or create schedule capacity
        schedule_capacity = CapacityService.get_or_create_schedule_capacity(
            db, schedule_id, schedule_date
        )

        if not schedule_capacity:
            return False, "Schedule does not operate on this date", None

        # Find overlapping segments
        overlapping_segments = CapacityService.find_overlapping_segments(
            db,
            schedule_capacity.id,
            origin_station_id,
            destination_station_id
        )

        if not overlapping_segments:
            return False, "No valid segments found for this route", None

        # Check capacity on each overlapping segment
        for segment in overlapping_segments:
            if train_class == TrainClass.First:
                available = segment.max_first_class - segment.first_class_load
            elif train_class == TrainClass.Second:
                available = segment.max_second_class - segment.second_class_load
            else:  # Third class
                available = segment.max_third_class - segment.third_class_load

            if available < num_passengers:
                reason = (
                    f"Insufficient capacity on segment {segment.origin_station} → "
                    f"{segment.destination_station}. Available: {available}, Requested: {num_passengers}"
                )
                logger.info(reason)
                return False, reason, segment

        # All segments have sufficient capacity
        return True, None, None

    @staticmethod
    def increment_segment_loads(
        db: Session,
        schedule_capacity_id: int,
        origin_station_id: str,
        destination_station_id: str,
        train_class: TrainClass,
        num_passengers: int = 1
    ):
        """
        Increment passenger load on all overlapping segments after successful booking

        Args:
            db: Database session
            schedule_capacity_id: Schedule capacity ID
            origin_station_id: Booking origin
            destination_station_id: Booking destination
            train_class: Train class
            num_passengers: Number of passengers
        """
        # Find overlapping segments
        overlapping_segments = CapacityService.find_overlapping_segments(
            db, schedule_capacity_id, origin_station_id, destination_station_id
        )

        # Increment load on each segment
        for segment in overlapping_segments:
            if train_class == TrainClass.First:
                segment.first_class_load += num_passengers
            elif train_class == TrainClass.Second:
                segment.second_class_load += num_passengers
            else:  # Third class
                segment.third_class_load += num_passengers

            # Update total load
            segment.total_load = (
                segment.first_class_load +
                segment.second_class_load +
                segment.third_class_load
            )

        # Update schedule capacity booking counters
        schedule_capacity = db.query(ScheduleCapacity).get(schedule_capacity_id)
        if schedule_capacity:
            if train_class == TrainClass.First:
                schedule_capacity.booked_first_class += num_passengers
            elif train_class == TrainClass.Second:
                schedule_capacity.booked_second_class += num_passengers
            else:  # Third class
                schedule_capacity.booked_third_class += num_passengers

            schedule_capacity.total_bookings += num_passengers

        db.commit()

        logger.info(
            f"Incremented load for {num_passengers} passengers in {train_class.value} class "
            f"on {len(overlapping_segments)} segments"
        )

    @staticmethod
    def decrement_segment_loads(
        db: Session,
        schedule_capacity_id: int,
        origin_station_id: str,
        destination_station_id: str,
        train_class: TrainClass,
        num_passengers: int = 1
    ):
        """
        Decrement passenger load on all overlapping segments after ticket cancellation/refund

        Args:
            db: Database session
            schedule_capacity_id: Schedule capacity ID
            origin_station_id: Booking origin
            destination_station_id: Booking destination
            train_class: Train class
            num_passengers: Number of passengers
        """
        # Find overlapping segments
        overlapping_segments = CapacityService.find_overlapping_segments(
            db, schedule_capacity_id, origin_station_id, destination_station_id
        )

        # Decrement load on each segment
        for segment in overlapping_segments:
            if train_class == TrainClass.First:
                segment.first_class_load = max(0, segment.first_class_load - num_passengers)
            elif train_class == TrainClass.Second:
                segment.second_class_load = max(0, segment.second_class_load - num_passengers)
            else:  # Third class
                segment.third_class_load = max(0, segment.third_class_load - num_passengers)

            # Update total load
            segment.total_load = (
                segment.first_class_load +
                segment.second_class_load +
                segment.third_class_load
            )

        # Update schedule capacity booking counters
        schedule_capacity = db.query(ScheduleCapacity).get(schedule_capacity_id)
        if schedule_capacity:
            if train_class == TrainClass.First:
                schedule_capacity.booked_first_class = max(0, schedule_capacity.booked_first_class - num_passengers)
            elif train_class == TrainClass.Second:
                schedule_capacity.booked_second_class = max(0, schedule_capacity.booked_second_class - num_passengers)
            else:  # Third class
                schedule_capacity.booked_third_class = max(0, schedule_capacity.booked_third_class - num_passengers)

            schedule_capacity.total_bookings = max(0, schedule_capacity.total_bookings - num_passengers)

        db.commit()

        logger.info(
            f"Decremented load for {num_passengers} passengers in {train_class.value} class "
            f"on {len(overlapping_segments)} segments"
        )

    @staticmethod
    def get_available_capacity_for_route(
        db: Session,
        schedule_id: str,
        schedule_date: date,
        origin_station_id: str,
        destination_station_id: str
    ) -> Dict[str, int]:
        """
        Get available capacity for each class on a specific route

        Args:
            db: Database session
            schedule_id: Train schedule ID
            schedule_date: Travel date
            origin_station_id: Origin station
            destination_station_id: Destination station

        Returns:
            Dictionary with available capacity per class
        """
        # First check if schedule operates on this date
        schedule = db.query(TrainSchedule).filter(
            TrainSchedule.train_schedule_id == schedule_id
        ).first()

        if not schedule:
            return {
                "first_class": 0,
                "second_class": 0,
                "third_class": 0,
                "error": "Schedule not found"
            }

        if not CapacityService.schedule_operates_on_date(schedule, schedule_date):
            return {
                "first_class": 0,
                "second_class": 0,
                "third_class": 0,
                "error": "Schedule does not operate on this date"
            }

        # Check if schedule capacity already exists
        schedule_capacity = db.query(ScheduleCapacity).filter(
            and_(
                ScheduleCapacity.schedule_id == schedule_id,
                ScheduleCapacity.schedule_date == schedule_date
            )
        ).first()

        # If capacity doesn't exist yet, return default capacity (no bookings yet)
        if not schedule_capacity:
            default_capacity = CapacityService.get_default_capacity(db, schedule_id)
            if not default_capacity:
                return {
                    "first_class": 0,
                    "second_class": 0,
                    "third_class": 0,
                    "error": "No default capacity configured"
                }

            # Return full default capacity (no bookings yet)
            first_capacity = CapacityService.calculate_class_capacity(
                default_capacity.first_class_compartments,
                default_capacity.seating_passengers_per_first_class,
                default_capacity.standing_passengers_per_first_class
            )
            second_capacity = CapacityService.calculate_class_capacity(
                default_capacity.second_class_compartments,
                default_capacity.seating_passengers_per_second_class,
                default_capacity.standing_passengers_per_second_class
            )
            third_capacity = CapacityService.calculate_class_capacity(
                default_capacity.third_class_compartments,
                default_capacity.seating_passengers_per_third_class,
                default_capacity.standing_passengers_per_third_class
            )

            return {
                "first_class": first_capacity,
                "second_class": second_capacity,
                "third_class": third_capacity,
                "total": first_capacity + second_capacity + third_capacity
            }

        # Schedule capacity exists, find overlapping segments
        overlapping_segments = CapacityService.find_overlapping_segments(
            db,
            schedule_capacity.id,
            origin_station_id,
            destination_station_id
        )

        if not overlapping_segments:
            return {
                "first_class": 0,
                "second_class": 0,
                "third_class": 0,
                "error": "No valid segments found for this route"
            }

        # Find bottleneck (segment with minimum available capacity)
        min_first = min(
            seg.max_first_class - seg.first_class_load
            for seg in overlapping_segments
        )
        min_second = min(
            seg.max_second_class - seg.second_class_load
            for seg in overlapping_segments
        )
        min_third = min(
            seg.max_third_class - seg.third_class_load
            for seg in overlapping_segments
        )

        return {
            "first_class": max(0, min_first),
            "second_class": max(0, min_second),
            "third_class": max(0, min_third),
            "total": max(0, min_first) + max(0, min_second) + max(0, min_third)
        }

    @staticmethod
    def confirm_schedule_capacity(
        db: Session,
        schedule_capacity_id: int,
        train_id: str
    ) -> bool:
        """
        Confirm schedule capacity with actual train assignment
        Called 24-48h before departure

        Args:
            db: Database session
            schedule_capacity_id: Schedule capacity ID
            train_id: Assigned train ID

        Returns:
            True if successful, False otherwise
        """
        schedule_capacity = db.query(ScheduleCapacity).get(schedule_capacity_id)

        if not schedule_capacity:
            logger.error(f"Schedule capacity {schedule_capacity_id} not found")
            return False

        # Get assigned train and its model
        train = db.query(OperationalTrain).filter(
            OperationalTrain.train_id == train_id
        ).first()

        if not train:
            logger.error(f"Train {train_id} not found")
            return False

        model = train.model

        # Get default capacity to determine compartments
        default_capacity = CapacityService.get_default_capacity(
            db, schedule_capacity.schedule_id
        )

        if not default_capacity:
            logger.error(
                f"No default capacity for schedule {schedule_capacity.schedule_id}"
            )
            return False

        # Calculate actual allocated capacity
        allocated_first = CapacityService.calculate_class_capacity(
            default_capacity.first_class_compartments,
            model.seating_passengers_per_compartment,
            model.standing_passengers_per_compartment
        )
        allocated_second = CapacityService.calculate_class_capacity(
            default_capacity.second_class_compartments,
            model.seating_passengers_per_compartment,
            model.standing_passengers_per_compartment
        )
        allocated_third = CapacityService.calculate_class_capacity(
            default_capacity.third_class_compartments,
            model.seating_passengers_per_compartment,
            model.standing_passengers_per_compartment
        )

        # Update schedule capacity
        schedule_capacity.train_id = train_id
        schedule_capacity.model_id = model.model_id
        schedule_capacity.allocation_status = AllocationStatus.Confirmed
        schedule_capacity.confirmed_at = datetime.now()

        schedule_capacity.allocated_first_class_compartments = default_capacity.first_class_compartments
        schedule_capacity.allocated_second_class_compartments = default_capacity.second_class_compartments
        schedule_capacity.allocated_third_class_compartments = default_capacity.third_class_compartments

        schedule_capacity.allocated_first_class_seats = allocated_first
        schedule_capacity.allocated_second_class_seats = allocated_second
        schedule_capacity.allocated_third_class_seats = allocated_third

        # Update segment capacities with actual train capacity
        segments = db.query(SegmentCapacity).filter(
            SegmentCapacity.schedule_capacity_id == schedule_capacity_id
        ).all()

        for segment in segments:
            segment.max_first_class = allocated_first
            segment.max_second_class = allocated_second
            segment.max_third_class = allocated_third
            segment.max_total = allocated_first + allocated_second + allocated_third

        db.commit()

        logger.info(
            f"Confirmed schedule capacity {schedule_capacity_id} with train {train_id} "
            f"(First: {allocated_first}, Second: {allocated_second}, Third: {allocated_third})"
        )

        return True


# Convenience functions for easy imports
def can_book_ticket(
    db: Session,
    schedule_id: str,
    schedule_date: date,
    origin_station_id: str,
    destination_station_id: str,
    train_class: TrainClass,
    num_passengers: int = 1
) -> Tuple[bool, Optional[str], Optional[SegmentCapacity]]:
    """Check if ticket can be booked"""
    return CapacityService.can_book_ticket(
        db, schedule_id, schedule_date, origin_station_id,
        destination_station_id, train_class, num_passengers
    )


def increment_segment_loads(
    db: Session,
    schedule_capacity_id: int,
    origin_station_id: str,
    destination_station_id: str,
    train_class: TrainClass,
    num_passengers: int = 1
):
    """Increment segment loads after booking"""
    return CapacityService.increment_segment_loads(
        db, schedule_capacity_id, origin_station_id,
        destination_station_id, train_class, num_passengers
    )


def get_available_capacity(
    db: Session,
    schedule_id: str,
    schedule_date: date,
    origin_station_id: str,
    destination_station_id: str
) -> Dict[str, int]:
    """Get available capacity for route"""
    return CapacityService.get_available_capacity_for_route(
        db, schedule_id, schedule_date, origin_station_id, destination_station_id
    )


def get_or_create_schedule_capacity(
    db: Session,
    schedule_id: str,
    schedule_date: date
) -> Optional[ScheduleCapacity]:
    """Get or create schedule capacity for a specific date"""
    return CapacityService.get_or_create_schedule_capacity(
        db, schedule_id, schedule_date
    )


def decrement_segment_loads(
    db: Session,
    schedule_capacity_id: int,
    origin_station_id: str,
    destination_station_id: str,
    train_class: TrainClass,
    num_passengers: int = 1
):
    """Decrement passenger loads when ticket is cancelled/refunded"""
    return CapacityService.decrement_segment_loads(
        db, schedule_capacity_id, origin_station_id, destination_station_id,
        train_class, num_passengers
    )
