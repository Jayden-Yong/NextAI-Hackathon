document.addEventListener("DOMContentLoaded", function(){
    // Prepare existing desks in layout
    desks = JSON.parse(document.getElementById('desks_json').textContent);
    booked = JSON.parse(document.getElementById('booked_json').textContent);
    // Prepare layout object
    layout = document.getElementById("map-layout");
    // Prepare selected desk object
    let selectedDesk = null;

    // Set deafult value for date to current date
    const dateInput = document.getElementById("date-input");
    const now = new Date();
    const formatDate = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
    dateInput.value = formatDate;
    dateInput.min = formatDate;
    // Redirect when dateInput is upadated
    dateInput.addEventListener('change', function() {
        console.log('Date input changed');
        const selectedDate = dateInput.value;
        fetch('/update_bookingData', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ selectedDate: selectedDate })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            renderLayout(desks,data.booked);

            const active = document.getElementById("active-counter");
            const member = document.getElementById("member-counter");
            active.textContent = data.active;
            member.textContent = data.active_members;
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while booking the desk.');
        });
    })

    // Desk selection logger
    function selectDesk(desk){
        // Remove highlight from previously selected desk
        if (selectedDesk) {
            selectedDesk.classList.remove('selected');
        }
        // Highlight the selected desk
        desk.classList.add('selected');
        selectedDesk = desk;

        errorText = document.getElementById("selectDeskError");
        errorText.classList.add("d-none");
    }
    // Remove selected desk when whitespace is clicked
    document.addEventListener('click', (event) => {
        if (selectedDesk && !event.target.classList.contains('selectable')) {
            selectedDesk.classList.remove('selected');
            selectedDesk = null;
        }
    });


    // Stop event propagation for the book button
    const bookButton = document.querySelector('.submit-btn');
    bookButton.addEventListener('click', (event) => {
        event.stopPropagation();
        bookDesk();
    });

    // Booking Logic
    window.bookDesk = function() {
        var isSelected = true;

        if (selectedDesk != null){
            const targetDesk = document.getElementById("deskID");
            const targetDate = document.getElementById("target-date");
            targetDesk.value = selectedDesk.getAttribute('data-id');
            targetDate.value = dateInput.value;
            
        } else {
            errorText = document.getElementById("selectDeskError");
            errorText.classList.remove("d-none");
            isSelected = false;
        }
        console.log(selectedDesk);

        return isSelected;
    }


    // Layout renderer
    function renderLayout(savedLayout, bookedList) {
        const layout = document.getElementById("map-layout");
        layout.innerHTML = "";  // Clear any existing items

        savedLayout.forEach(item => {
            let booked = false;
            const element = document.createElement("img");
            element.src = item.deskID.startsWith("D") ? "/static/images/desk.png" : "/static/images/meeting_unavailable.png";

            // Sets the element to unavailable when found in booked list
            for (let booking of bookedList){
                if (booking.deskID == item.deskID){
                    element.src = item.deskID.startsWith("D") ? "/static/images/desk_unavailable.png" : "/static/images/meeting-room.png";
                    booked = true;
                    break;
                }
            }
            
            element.classList.add("selectable");
            element.setAttribute("data-id", item.deskID);
            element.style.width = item.deskID.startsWith("D") ? "80px" : "120px";
            element.style.height = item.deskID.startsWith("D") ? "80px" : "120px";
            element.style.position = "absolute";
            element.style.left = item.coordX + "px";
            element.style.top = item.coordY + "px";
            layout.appendChild(element);

            if (!booked && item.deskID.startsWith("D")) {element.addEventListener('click', () => selectDesk(element));}
        });

        
    }

    renderLayout(desks,booked);
});