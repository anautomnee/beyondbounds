const group_id = window.location.pathname.split('/').slice(-1)[0];

let calendarEl = document.getElementById('calendar');
let calendar = new FullCalendar.Calendar(calendarEl,{
    initialView: 'timeGridWeek',
    selectable: true,
    headerToolbar: {
        center: 'addEventButton, hideMyEvents'
    },
    customButtons: {
        addEventButton: {
            text: 'Save changes',

            click: async function() {
                let allEvents = calendar.getEvents()
                
                // Make a request to insert new events into database
                for (const event of allEvents) {
                    // Skip if event is known
                    if (event.id) continue;

                    const formData = new FormData();
                    formData.append("start", event.start.toISOString());
                    formData.append("end", event.end.toISOString());

                    // Get group_id from URL
                    formData.append("group_id", group_id);
                
                    try {
                        const response = await fetch("/api/newevent", {
                            method: "POST",
                            body: formData
                        });
                        await response.text().then(id => event.setProp("id", id));
                        // Setting event as not editable as have already been saved
                        event.setProp("editable", false)
                    }
                    catch (error) {
                        console.error('Failed to push event: ', error);
                    }

                }
            }
        },
        hideMyEvents: {
            text: 'Hide my events',
            events: `/api/hidemyevents?group_id=${group_id}`,
        }
    },
    // Download old events for this group
    events: `/api/getevents?group_id=${group_id}`,

    // New events
    select: async function(info) {

        calendar.addEvent({
            start: info.start,
            end: info.end,
            editable: true,
        });
    }
});
calendar.render();
