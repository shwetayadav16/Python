const state = {
    events: [],
};

const elements = {
    eventsGrid: document.getElementById("eventsGrid"),
    eventSelect: document.getElementById("eventSelect"),
    bookingForm: document.getElementById("bookingForm"),
    formMessage: document.getElementById("formMessage"),
    bookingsList: document.getElementById("bookingsList"),
    eventCount: document.getElementById("eventCount"),
    customerName: document.getElementById("customerName"),
    email: document.getElementById("email"),
    tickets: document.getElementById("tickets"),
};

function formatPrice(amount) {
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 0,
    }).format(amount);
}

function renderEvents() {
    elements.eventsGrid.innerHTML = state.events
        .map(
            (event) => `
                <article class="event-card">
                    <div class="event-card-top">
                        <span class="pill">${event.category}</span>
                        <strong>${formatPrice(event.price)}</strong>
                    </div>
                    <h3>${event.title}</h3>
                    <p>${event.description}</p>
                    <ul class="event-meta">
                        <li>${event.event_date} at ${event.event_time}</li>
                        <li>${event.venue}</li>
                        <li>${event.seats_available} seats left</li>
                    </ul>
                </article>
            `
        )
        .join("");

    elements.eventSelect.innerHTML = state.events
        .map(
            (event) => `
                <option value="${event.id}">
                    ${event.title} - ${formatPrice(event.price)} - ${event.seats_available} seats left
                </option>
            `
        )
        .join("");

    elements.eventCount.textContent = `${state.events.length} events`;
}

function renderBookings(bookings) {
    if (!bookings.length) {
        elements.bookingsList.innerHTML = "<p class='empty-state'>No bookings yet. Be the first one.</p>";
        return;
    }

    elements.bookingsList.innerHTML = bookings
        .map(
            (booking) => `
                <article class="booking-item">
                    <div>
                        <h3>${booking.customer_name}</h3>
                        <p>${booking.event_title}</p>
                    </div>
                    <div class="booking-side">
                        <strong>${booking.tickets} tickets</strong>
                        <span>${formatPrice(booking.total_price)}</span>
                    </div>
                </article>
            `
        )
        .join("");
}

async function loadEvents() {
    const response = await fetch("/api/events");
    state.events = await response.json();
    renderEvents();
}

async function loadBookings() {
    const response = await fetch("/api/bookings");
    const bookings = await response.json();
    renderBookings(bookings);
}

function setMessage(message, isError = false) {
    elements.formMessage.textContent = message;
    elements.formMessage.className = isError ? "form-message error" : "form-message success";
}

async function submitBooking(event) {
    event.preventDefault();

    const payload = {
        event_id: elements.eventSelect.value,
        customer_name: elements.customerName.value.trim(),
        email: elements.email.value.trim(),
        tickets: elements.tickets.value,
    };

    const response = await fetch("/api/book", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    const result = await response.json();

    if (!response.ok) {
        setMessage(result.error || "Booking failed.", true);
        return;
    }

    setMessage(`${result.message} Total: ${formatPrice(result.total_price)}`);
    elements.bookingForm.reset();
    elements.tickets.value = 1;
    await Promise.all([loadEvents(), loadBookings()]);
}

async function init() {
    await Promise.all([loadEvents(), loadBookings()]);
    elements.bookingForm.addEventListener("submit", submitBooking);
}

init().catch(() => {
    setMessage("Unable to load event data right now.", true);
});
