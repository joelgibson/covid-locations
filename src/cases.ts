/** Some definitions so we can strongly type the JSON. */
export type CasesJSON = {
    date: string
    title: string
    data: {
        monitor: CaseJSON[]
    }
}
type CaseJSON = {
    Venue: string
    Address: string
    Suburb: string
    Date: string
    Time: string
    Alert: string
    Lon: string
    Lat: string
    HealthAdviceHTML: string
    'Last updated date': string
}

/** Parse the "Date" field of a CaseJSON. */
function parseDate(date: string) {
    const months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'];
    let match = date.match(/([0-9][0-9]?)\s+([a-zA-Z]+)\s+([0-9]{4})/)
    if (match == null)
        throw new Error(`Date was not matched: '${date}'`)
    
    let year = +match[3]
    let month = months.indexOf(match[2].slice(0, 3).toLowerCase())
    let day = +match[1]

    return {year, month, day}
}

/** Parse the "Time" field of a CaseJSON */
function parseTime(time: string) {
    if (time == 'All day' || time == '')
        return {hours: 0, minutes: 0}
    
    let match = time.match(/([0-9]{1,2})(?::([0-9]{2}))?(am|pm)/)
    if (match == null)
        throw new Error(`Time was not matched: '${time}'`)
    
    let hours = +match[1]
    if (match[3] == 'pm' && hours != 12)
        hours += 11
    let minutes = +(match[2] || '0') // If match[2] is empty string, this is zero.
    if (minutes.toString() == 'NaN')
        throw new Error("Minutes was NaN")
    return {hours, minutes}
}

/** Extract a "first time" from a CaseJSON, defaulting to midnight if the time is "All Day". */
export function firstTime(data: CaseJSON): Date {
    let {year, month, day} = parseDate(data.Date)
    let {hours, minutes} = parseTime(data.Time)
    let date = new Date(year, month, day, hours, minutes)
    if (date.toString() == 'Invalid Date')
        throw new Error("Date was invalid")
    
    return date
}

