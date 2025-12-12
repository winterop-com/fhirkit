/*
 * Intervals - Working with date/time intervals
 */
library Intervals version '1.0.0'

using FHIR version '4.0.1'

// Date intervals
define CurrentYear: Interval[@2024-01-01, @2024-12-31]

define LastMonth: Interval[Today() - 1 month, Today()]

define Last30Days: Interval[Today() - 30 days, Today()]

// DateTime intervals
define WorkingHours: Interval[@T09:00:00, @T17:00:00]

// Open/closed intervals
define OpenInterval: Interval(0, 10)     // exclusive bounds
define ClosedInterval: Interval[0, 10]   // inclusive bounds
define MixedInterval: Interval[0, 10)    // left inclusive, right exclusive

// Interval operations
define IntervalWidth: width of Interval[1, 10]

define IntervalStart: start of Interval[@2024-01-01, @2024-12-31]

define IntervalEnd: end of Interval[@2024-01-01, @2024-12-31]

// Interval relationships
define TestOverlaps: Interval[1, 5] overlaps Interval[3, 8]

define TestContains: Interval[1, 10] includes Interval[3, 7]

define TestDuring: 5 in Interval[1, 10]
