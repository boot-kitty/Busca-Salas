const days = ['L', 'M', 'W', 'J', 'V', 'S'];
const times = [1, 2, 3, 4, 5, 6, 7, 8, 9];
let selectedSlots = new Set();
let data = [];

function initTimetable() {
    const timetable = document.getElementById('timetable');
    
    times.forEach(time => {
        const timeHeader = document.createElement('div');
        timeHeader.className = 'header';
        timeHeader.textContent = time;
        timetable.appendChild(timeHeader);

        days.forEach(day => {
            const slot = document.createElement('div');
            slot.className = 'time-slot';
            slot.dataset.day = day;
            slot.dataset.time = time;
            slot.onclick = () => toggleSlot(slot);
            timetable.appendChild(slot);
        });
    });
}

function toggleSlot(slot) {
    const key = `${slot.dataset.day}-${slot.dataset.time}`;
    if (selectedSlots.has(key)) {
        selectedSlots.delete(key);
        slot.classList.remove('selected');
    } else {
        selectedSlots.add(key);
        slot.classList.add('selected');
    }
    filterResults();
}

function filterResults() {
    if (selectedSlots.size === 0) {
        document.getElementById('results').innerHTML = '<p>Selecciona horarios para ver lugares disponibles</p>';
        return;
    }

    const selectedDays = new Set();
    const selectedTimes = new Set();
    
    selectedSlots.forEach(slot => {
        const [day, time] = slot.split('-');
        selectedDays.add(day);
        selectedTimes.add(parseInt(time));
    });

    const availablePlaces = data.filter(place => {
        return Array.from(selectedDays).every(day => 
            Array.from(selectedTimes).every(time => 
                place.horarios[day] && place.horarios[day].includes(time)
            )
        );
    });

    const resultsDiv = document.getElementById('results');
    if (availablePlaces.length === 0) {
        resultsDiv.innerHTML = '<p>No hay salas disponibles para la selección actual</p>';
    } else {
        resultsDiv.innerHTML = availablePlaces
            .sort((a, b) => a.nombre.localeCompare(b.nombre))
            .map(place => `<span class="place">${place.nombre}</span>`)
            .join('');
    }
}

function clearSelection() {
    selectedSlots.clear();
    document.querySelectorAll('.time-slot').forEach(slot => {
        slot.classList.remove('selected');
    });
    filterResults();
}

function selectAll() {
    selectedSlots.clear();
    document.querySelectorAll('.time-slot').forEach(slot => {
        const key = `${slot.dataset.day}-${slot.dataset.time}`;
        selectedSlots.add(key); 
        slot.classList.add('selected');
    });
    filterResults();
}

async function loadData() {
    const selector = document.getElementById('dataSelector');
    const selectedValue = selector.value;
    
    try {
        const origin = window.location.origin + window.location.pathname;
        const response = await fetch(`${origin}/database/${selectedValue}.json`);
        await console.log(response.json)
        data = await response.json();
        clearSelection();
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initTimetable();
    loadData();
});