document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    const userId = localStorage.getItem('userId');
    const username = localStorage.getItem('username');
    
    if (!userId) {
        window.location.href = 'login.html';
        return;
    }

    // Set user greeting
    const userGreeting = document.getElementById('userGreeting');
    if (userGreeting) {
        userGreeting.textContent = `Welcome, ${username}!`;
    }

    // Logout handler
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('userId');
            localStorage.removeItem('username');
            window.location.href = 'login.html';
        });
    }

    // Load hotels for the select dropdown
    const loadHotels = async () => {
        try {
            const response = await fetch('/api/hotels');
            const hotels = await response.json();
            
            const hotelSelect = document.getElementById('hotelSelect');
            hotels.forEach(hotel => {
                const option = document.createElement('option');
                option.value = hotel.id;
                option.textContent = `${hotel.name} (${hotel.rating}⭐)`;
                hotelSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading hotels:', error);
        }
    };

    // Load user's bookings
    const loadBookings = async () => {
        try {
            const response = await fetch(`/api/bookings?user_id=${userId}`);
            const bookings = await response.json();
            
            const bookingsList = document.getElementById('bookingsList');
            bookingsList.innerHTML = '';

            bookings.forEach(booking => {
                const bookingElement = document.createElement('div');
                bookingElement.className = 'booking-card';
                bookingElement.innerHTML = `
                    <h3>${booking.hotel_name}</h3>
                    <p>From: ${new Date(booking.start_date).toLocaleDateString()}</p>
                    <p>To: ${new Date(booking.end_date).toLocaleDateString()}</p>
                    <button class="btn-danger delete-booking" data-id="${booking.id}">Cancel Booking</button>
                `;
                bookingsList.appendChild(bookingElement);
            });

            // Add delete handlers
            document.querySelectorAll('.delete-booking').forEach(button => {
                button.addEventListener('click', showDeleteDialog);
            });
        } catch (error) {
            console.error('Error loading bookings:', error);
        }
    };

    // Booking form handler
    const bookingForm = document.getElementById('bookingForm');
    if (bookingForm) {
        bookingForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const hotelId = document.getElementById('hotelSelect').value;
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;

            try {
                const response = await fetch('/api/bookings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_id: userId,
                        hotel_id: hotelId,
                        start_date: startDate,
                        end_date: endDate
                    }),
                });

                if (response.ok) {
                    alert('Booking successful!');
                    bookingForm.reset();
                    loadBookings();
                } else {
                    const data = await response.json();
                    alert(data.message || 'Booking failed');
                }
            } catch (error) {
                alert('Error creating booking. Please try again.');
            }
        });
    }

    // Delete dialog handlers
    let currentBookingId = null;
    
    function showDeleteDialog(e) {
        const dialog = document.getElementById('deleteDialog');
        const overlay = document.getElementById('overlay');
        currentBookingId = e.target.dataset.id;
        
        dialog.style.display = 'block';
        overlay.style.display = 'block';
    }

    document.getElementById('cancelDelete').addEventListener('click', () => {
        const dialog = document.getElementById('deleteDialog');
        const overlay = document.getElementById('overlay');
        
        dialog.style.display = 'none';
        overlay.style.display = 'none';
        currentBookingId = null;
    });

    document.getElementById('confirmDelete').addEventListener('click', async () => {
        if (!currentBookingId) return;

        try {
            const response = await fetch(`/api/bookings/${currentBookingId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                const dialog = document.getElementById('deleteDialog');
                const overlay = document.getElementById('overlay');
                
                dialog.style.display = 'none';
                overlay.style.display = 'none';
                
                loadBookings();
            } else {
                alert('Error deleting booking');
            }
        } catch (error) {
            alert('Error deleting booking. Please try again.');
        }
    });

    // Initialize page
    loadHotels();
    loadBookings();
});