document.addEventListener("DOMContentLoaded", function() {
    // Prepare existing desks in layout
    desks = JSON.parse(document.getElementById('desks_json').textContent);
    console.log(desks);
    booked = JSON.parse(document.getElementById('booked_json').textContent);
    // Prepare layout object
    layout = document.getElementById("map-layout");
    // Prepare selected desk object
    let selectedDesk = null;


    // Set deafult value for date to current date
    const datetimeInput = document.getElementById("date-input");
    const duration = document.getElementById("duration-input");
    const now = new Date();
    const formatDate = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    datetimeInput.value = formatDate;
    datetimeInput.min = formatDate;

    // Redirect when datetimeInput is upadated
    datetimeInput.addEventListener('change', function() {
        console.log('Date input changed');
        const selectedDatetime = datetimeInput.value;
        const selectedDuration = duration.value;
        fetch('/update_meeting_bookingData', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ selectedDatetime: selectedDatetime, duration: selectedDuration })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            renderLayout(desks,data.booked);

            const active = document.getElementById("active-counter");
            const member = document.getElementById("member-counter");
            active.textContent = data.total_booked;
            member.textContent = data.total_left;
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while booking the desk.');
        });
    })

    // Redirect when duration is upadated
    duration.addEventListener('change', function() {
        console.log('Date input changed');
        const selectedDatetime = datetimeInput.value;
        const selectedDuration = document.getElementById("duration-input").value;
        fetch('/update_meeting_bookingData', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ selectedDatetime: selectedDatetime, duration: selectedDuration })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            renderLayout(desks,data.booked);

            const active = document.getElementById("active-counter");
            const member = document.getElementById("member-counter");
            active.textContent = data.total_booked;
            member.textContent = data.total_left;
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
            const targetDesk = document.getElementById("meetingID");
            const targetStart = document.getElementById("target-start");
            const targetDuration = document.getElementById("duration")
            targetDesk.value = selectedDesk.getAttribute('data-id');
            targetStart.value = datetimeInput.value;
            targetDuration.value = duration.value;
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
            element.src = item.deskID.startsWith("M") ? "/static/images/meeting-room.png" : "/static/images/desk_unavailable.png";

            // Sets the element to unavailable when found in booked list
            for (let booking of bookedList){
                if (booking.deskID == item.deskID){
                    element.src = item.deskID.startsWith("M") ? "/static/images/meeting_unavailable.png" : "/static/images/desk_unavailable.png";
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

            if (!booked && item.deskID.startsWith("M")) {element.addEventListener('click', () => selectDesk(element));}
        }); 
    }

    renderLayout(desks,booked);

});