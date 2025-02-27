document.addEventListener("DOMContentLoaded", function() {
    // Get existing desks from json
    desks = JSON.parse(document.getElementById('desks_json').textContent);
    console.log(desks)
    // Creates layout object
    layout = document.getElementById("layout");
    // Calculate layout dimensions
    const layoutWidth = layout.offsetWidth;
    const layoutHeight = layout.offsetHeight;
    // Define item dimensions and spacing
    const deskWidth = 80;
    const deskHeight = 80;
    const meetingWidth = 120;
    const meetingHeight = 120;
    const padding = 20;
    let selectedDesk = null;

    // Listener to update the element's translation on drag
    function dragMoveListener(event) {
        const target = event.target;
        // Use custom attributes to keep track of the translation
        const x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
        const y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

        // Apply the translation via CSS transform
        target.style.transform = 'translate(' + x + 'px, ' + y + 'px)';

        // Update the position attributes
        target.setAttribute('data-x', x);
        target.setAttribute('data-y', y);

        // Update the coordinates in the desks array
        const deskID = target.getAttribute('data-id');
        desks.forEach(desk => {
            if (desk.deskID == deskID){
                desk.coordX = x;
                desk.coordY = y;
            }
        });
    }

    function idGenerator(){
        let i, isCreated = true;
        while(isCreated){
            i = Math.floor(Math.random() * (100 - 1 + 1)) + 1;
            let idExists = false;
            desks.forEach(desk => {
                id = parseInt(desk.deskID.substring(1), 10);
                if (i == id) {
                    idExists = true;
                }
            });
            if (!idExists) {
                isCreated = false;
            }
        }
        return i;
    }

    // Function to recreate the layout from saved data
    function renderLayout(savedLayout) {
        const layout = document.getElementById("layout");
        layout.innerHTML = "";  // Clear any existing items

        savedLayout.forEach(item => {
            const element = document.createElement("img");
            element.src = item.deskID.startsWith("D") ? "/static/images/desk.png" : "/static/images/meeting-room.png";
            element.classList.add("draggable");
            element.setAttribute("data-id", item.deskID);
            element.style.width = item.deskID.startsWith("D") ? "80px" : "120px";
            element.style.height = item.deskID.startsWith("D") ? "80px" : "120px";
            element.style.position = "absolute";
            element.style.left = item.coordX + "px";
            element.style.top = item.coordY + "px";
            layout.appendChild(element);

            element.addEventListener('click', () => selectDesk(element));
        });

        // Initialize drag functionality
        interact('.draggable').draggable({
            inertia: true,
            modifiers: [
                interact.modifiers.restrictRect({
                    restriction: 'parent',
                    endOnly: true
                })
            ],
            autoScroll: true,
            listeners: {
                move: dragMoveListener
            }
        });
    }

    // Function to add a desk
    window.createDesk = function() {
        const desk = document.createElement("img");
        const i = idGenerator();
        desk.src = "/static/images/desk.png";
        desk.classList.add("draggable");
        desk.setAttribute("data-id", "D" + i);
        desk.style.width = deskWidth + "px";
        desk.style.height = deskHeight + "px";
        desk.style.position = "absolute";

        let x, y, isOccupied;
        do{
            isOccupied = false;
            x = Math.floor(Math.random() * (layoutWidth - deskWidth - padding * 2)) + padding;
            y = Math.floor(Math.random() * (layoutHeight - deskHeight - padding * 2)) + padding;

            // Check if the position is occupied
            for (const desk of desks) {
                if (Math.abs(desk.coordX - x) < deskWidth && Math.abs(desk.coordY - y) < deskHeight) {
                    isOccupied = true;
                    break;
                }
            }

        } while (isOccupied);

        // Only place the desk if it fits within the layout and an empty spot was found
        if (!isOccupied && y + deskHeight <= layoutHeight - padding) {
            desk.style.left = x + "px";
            desk.style.top = y + "px";
            
            // Add the new desk to the array of desks
            desks.push({
                deskID: "D" + i,
                coordX: x,
                coordY: y
            });

            const counter = document.getElementById("desk_count");
            const count = parseInt(counter.textContent, 10) + 1;
            counter.textContent = count;

            // Append the new desk to the layout without re-rendering the entire layout
            layout.appendChild(desk);

            // Initialize drag functionality for the new desk
            interact(desk).draggable({
                inertia: true,
                modifiers: [
                    interact.modifiers.restrictRect({
                        restriction: 'parent',
                        endOnly: true
                    })
                ],
                autoScroll: true,
                listeners: {
                    move: dragMoveListener
                }
            });

            desk.addEventListener('click', () => selectDesk(desk));

        } else {
            console.log("Failed to find an empty spot for the new desk.");
        }
    }

    window.createMeeting = function() {
        const meeting = document.createElement("img");
        const i = idGenerator();
        meeting.src = "/static/images/meeting-room.png";
        meeting.classList.add("draggable");
        meeting.setAttribute("data-id", "M" + i);
        meeting.style.width = meetingWidth + "px";
        meeting.style.height = meetingHeight + "px";
        meeting.style.position = "absolute";

        let x, y, isOccupied;
        do{
            isOccupied = false;
            x = Math.floor(Math.random() * (layoutWidth - meetingWidth - padding * 2)) + padding;
            y = Math.floor(Math.random() * (layoutHeight - meetingHeight - padding * 2)) + padding;

            // Check if the position is occupied
            for (const desk of desks) {
                if (Math.abs(desk.coordX - x) < meetingWidth && Math.abs(desk.coordY - y) < meetingHeight) {
                    isOccupied = true;
                    break;
                }
            }

        } while (isOccupied);

        // Only place the desk if it fits within the layout and an empty spot was found
        if (!isOccupied && y + meetingHeight <= layoutHeight - padding) {
            meeting.style.left = x + "px";
            meeting.style.top = y + "px";
            
            // Add the new desk to the array of desks
            desks.push({
                deskID: "M" + i,
                coordX: x,
                coordY: y
            });

            const counter = document.getElementById("meeting_count");
            const count = parseInt(counter.textContent, 10) + 1;
            counter.textContent = count;

            // Append the new desk to the layout without re-rendering the entire layout
            layout.appendChild(meeting);

            // Initialize drag functionality for the new meeting
            interact(meeting).draggable({
                inertia: true,
                modifiers: [
                    interact.modifiers.restrictRect({
                        restriction: 'parent',
                        endOnly: true
                    })
                ],
                autoScroll: true,
                listeners: {
                    move: dragMoveListener
                }
            });

            meeting.addEventListener('click', () => selectDesk(meeting));

        } else {
            console.log("Failed to find an empty spot for the new meeting room.");
        }
    }

    function selectDesk(desk){
        // Remove highlight from previously selected desk
        if (selectedDesk) {
            selectedDesk.classList.remove('selected');
        }
        // Highlight the selected desk
        desk.classList.add('selected');
        selectedDesk = desk;
    }

    // Function to delete the selected desk
    window.deleteSelectedDesk = function() {
        if (selectedDesk) {
            const deskID = selectedDesk.getAttribute('data-id');
            // Remove the desk from the desks array
            desks = desks.filter(desk => desk.deskID !== deskID);
            console.log(desks);
            // Remove the desk from the layout
            selectedDesk.remove();
            selectedDesk = null;

            // Update the desk count
            target_count = deskID.startsWith('D') ? "desk_count" : "meeting_count";
            const counter = document.getElementById(target_count);
            const count = parseInt(counter.textContent, 10) - 1;
            counter.textContent = count;
        }
    }

    window.saveLayout = function() {
        const items = document.querySelectorAll('.draggable');
        const layoutData = [];

        items.forEach(item => {
            const id = item.getAttribute("data-id");
            // Calculate final position: original offset plus translation
            const rect = item.getBoundingClientRect();
            const parentRect = document.getElementById("layout").getBoundingClientRect();
            const x = rect.left - parentRect.left;
            const y = rect.top - parentRect.top;

            layoutData.push({ id: id, coordX: Math.round(x), coordY: Math.round(y) });
        });

        console.log(layoutData)

        // Send the data to the Flask endpoint via POST request
        fetch('/save_layout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(layoutData)
        })
            .then(response => response.json())
            .then(data => {
                alert('Layout saved successfully!');
            })
            .catch(error => {
                console.error('Error saving layout:', error);
            });
    }

    document.addEventListener('click', (event) => {
        if (selectedDesk && !event.target.classList.contains('draggable')) {
            selectedDesk.classList.remove('selected');
            selectedDesk = null;
        }
    });

    // Main Control Module

    if (desks.length === 0){
    } else {
            renderLayout(desks);
    }
});