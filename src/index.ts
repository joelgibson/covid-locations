import {CasesJSON, firstTime} from './cases'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import casesUntyped from './covid-case-locations-20210630-200.json'

let cases = casesUntyped as CasesJSON

// Extract the case data, merge in the "firstTime", and sort by increasing firstTime.
let caseData = cases.data.monitor
    .map(data => ({...data, firstTime: firstTime(data)}))
    .sort((a, b) => a.firstTime.getTime() - b.firstTime.getTime())

// Create a map centred on Sydney.
let map = L.map('mapid').setView([-33.88478871765595, 151.2260430608038], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    opacity: 0.8,
}).addTo(map);

// Create a marker object for each case, not yet added to the map.
// The tooltip should be the date, time, and location.
let markers = caseData.map(data => {
    return L.circleMarker([+data.Lat, +data.Lon], {radius: 10})
        .bindTooltip(`${data.Date}, ${data.Time}\n${data.Venue}`)
})
let bigMarkers = caseData.map(data => L.circleMarker([+data.Lat, +data.Lon], {radius: 50, fill: false, color: 'red'}))
bigMarkers.forEach(marker => marker.addTo(map))

// Given a time, return the index i so that caseData[0], ..., caseData[i-1] are all
// less than time.
function insertionPoint(time: Date) {
    for (let i = 0; i < caseData.length; i++)
        if (caseData[i].firstTime.getTime() >= time.getTime())
            return i
    
    return caseData.length
}

let {setState, getState, rangeInput} = (function() {
    // minTime corresponds to 0.0
    let minTime = caseData[0].firstTime

    // maxTime to 1.0. (Go six hours after the last datapoint, so we can see it properly).
    let maxTime = new Date(caseData[caseData.length - 1].firstTime.getTime() + 1000 * 60 * 60 * 6)
    let deltams = maxTime.getTime() - minTime.getTime()

    // I/O
    let rangeInput = document.getElementById('rangeInput') as HTMLInputElement
    let spanOutput = document.getElementById('date') as HTMLSpanElement

    // Internal memory of the last state.
    let state = 0.0

    return {setState, getState() { return state }, rangeInput}

    function stateToDate(state: number): Date {
        return new Date(minTime.getTime() + deltams * state)
    }
    
    function applyStateChange(oldState: number, newState: number) {
        let oldIndex = insertionPoint(stateToDate(oldState))
        let newTime = stateToDate(newState)
        let newIndex = insertionPoint(newTime)
    
        // The set of elements shown should be [0, ..., newIndex)
        if (oldIndex == newIndex) {}
        else if (oldIndex < newIndex) {
            // We only need to add items
            for (let i = oldIndex; i < newIndex; i++)
                markers[i].addTo(map)
        } else {
            for (let i = newIndex; i < oldIndex; i++)
                markers[i].remove()
        }
    
        // Set the opacity of the big markers to zero unless they are less than a day behind the current time.
        // For those that are within a day behind, scale their size and opacity appropriately.
        for (let i = 0; i < bigMarkers.length; i++) {
            let days = (newTime.getTime() - caseData[i].firstTime.getTime()) / (1000 * 60 * 60 * 24)
            bigMarkers[i].setRadius(40 / (1 + days))
            bigMarkers[i].setStyle({opacity: (days >= 0) ? Math.max(0, 1 - days) : 0})
        }
    
        rangeInput.value = `${newState}`
        spanOutput.innerText = new Intl.DateTimeFormat('en-GB', { dateStyle: 'full', timeStyle: 'short' }).format(newTime);
    }

    function setState(newState: number) {
        applyStateChange(state, newState)
        state = newState
    }
})()

// Set up animation button.
let {playAnimation, pauseAnimation} = (function() {
    let targetTime = 15 * 1000
    let interval: null | number = null
    let lastTick = new Date()
    let lastState = 0

    let button = document.getElementById('animate') as HTMLButtonElement
    button.addEventListener('click', () => (interval === null) ? playAnimation() : pauseAnimation());

    return {playAnimation, pauseAnimation}

    function playAnimation() {
        // If there is an animation going, do nothing.
        if (interval !== null)
            return
        
        lastState = getState()
        if (lastState >= 1.0)
            lastState = 0.0
        setState(lastState)
        lastTick = new Date()
        interval = setInterval(tickAnimation, 10)
        button.innerText = 'Pause'
    }

    function pauseAnimation() {
        if (interval === null)
            return
        
        clearInterval(interval)
        interval = null
        button.innerText = 'Play'
    }

    function tickAnimation() {
        let now = new Date()
        let delta = (now.getTime() - lastTick.getTime()) / targetTime
        let newState = Math.min(1, lastState + delta)
        setState(newState)

        if (newState >= 1) {
            pauseAnimation()
            button.innerText = 'Restart'
        }
        
        lastTick = now
        lastState = newState
    }
})()

// Selecting using the range input
rangeInput.addEventListener('input', () => {
    pauseAnimation()
    setState(+rangeInput.value)
})

// Initial setup
setState(0.0)
pauseAnimation()

// Activate animation when range is first scrolled into view. The callback checks for any intersection,
// then starts the animation and disconnects the observer.
let observer = new IntersectionObserver(function(entries, observer) {
    for (let entry of entries) {
        if (!entry.isIntersecting)
            continue

        playAnimation()
        observer.disconnect()
        return
    }
}).observe(rangeInput)