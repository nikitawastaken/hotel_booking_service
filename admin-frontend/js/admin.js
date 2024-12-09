// Check authentication
if (!localStorage.getItem('adminLoggedIn')) {
    window.location.href = 'admin-login.html';
}

// Logout functionality
document.getElementById('logoutBtn').addEventListener('click', () => {
    localStorage.removeItem('adminLoggedIn');
    window.location.href = 'admin-login.html';
});

// Hotels Management
async function loadHotels() {
    const response = await fetch('/api/hotels');
    const hotels = await response.json();
    
    const hotelsList = document.getElementById('hotelsList');
    hotelsList.innerHTML = hotels.map(hotel => `
        <div class="data-item">
            <span>${hotel.name} (Rating: ${hotel.rating})</span>
            <button onclick="deleteHotel(${hotel.id})">Delete</button>
        </div>
    `).join('');
}

async function deleteHotel(id) {
    if (confirm('Are you sure you want to delete this hotel?')) {
        await fetch(`/api/admin/hotels/${id}`, { method: 'DELETE' });
        loadHotels();
        loadUsers();
    }
}

document.getElementById('addHotelForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('hotelName').value;
    const rating = document.getElementById('hotelRating').value;
    
    await fetch('/api/admin/hotels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, rating })
    });
    
    document.getElementById('addHotelForm').reset();
    loadHotels();
});

// Users Management
async function loadUsers() {
    const response = await fetch('/api/admin/users');
    const users = await response.json();
    
    const usersList = document.getElementById('usersList');
    usersList.innerHTML = users.map(user => `
        <div class="data-item">
            <span>${user.username} (Bookings: ${user.booking_count})</span>
            <div>
                <button onclick="viewUserBookings(${user.id})">View Bookings</button>
                <button onclick="deleteUser(${user.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

async function deleteUser(id) {
    if (confirm('Are you sure you want to delete this user?')) {
        await fetch(`/api/admin/users/${id}`, { method: 'DELETE' });
        loadUsers();
    }
}

// Bookings Modal
const modal = document.getElementById('bookingsModal');
const closeBtn = document.getElementsByClassName('close')[0];

closeBtn.onclick = () => modal.style.display = "none";
window.onclick = (e) => {
    if (e.target == modal) modal.style.display = "none";
}

async function viewUserBookings(userId) {
    const response = await fetch(`/api/admin/users/${userId}/bookings`);
    const bookings = await response.json();
    
    document.getElementById('userBookings').innerHTML = bookings.map(booking => `
        <div class="data-item">
            <div>
                <strong>${booking.hotel_name}</strong><br>
                ${new Date(booking.start_date).toLocaleDateString()} - 
                ${new Date(booking.end_date).toLocaleDateString()}
            </div>
        </div>
    `).join('');
    
    modal.style.display = "block";
}

// Initial load
loadHotels();
loadUsers();