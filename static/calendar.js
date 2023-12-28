const group_id = window.location.pathname.split("/").slice(-1)[0];

let areMyEventsHidden = false;

let calendarEl = document.getElementById("calendar");
let calendar = new FullCalendar.Calendar(calendarEl,{
    initialView: "timeGridWeek",
    selectable: true,
    unselectAuto: false,
    headerToolbar: {
        center: "addEventButton hideMyEvents"
    },
    customButtons: {
        addEventButton: {
            text: "Save changes",

            click: async function(_, button) {
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
                        event.setProp("editable", false);
                        event.setProp("color", "#FD8F52");
                    }
                    catch (error) {
                        console.error("Failed to push event: ", error);
                    }
                }
                button.hidden = true;
            }
        },
        hideMyEvents: {
            text: "Hide my events",
            click: (_, button) => {
                const allEvents = calendar.getEvents();
                
                for (const event of allEvents) {
                    if (event.display === "background") continue;
                    if (areMyEventsHidden === true) {
                        event.setProp("display", "auto");
                    }
                    else {
                        event.setProp("display", "none");
                    }
                }

                areMyEventsHidden = !areMyEventsHidden;
                button.innerHTML = `${areMyEventsHidden ? "Show" : "Hide"} my events`;
            }
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
        document.querySelector('button[title="Save changes"]').hidden = false;
    },
    unselect: function () {
        for (const event of calendar.getEvents()) {
            if (!event.id) event.remove();
        }
    }
});
calendar.render();

document.querySelector('button[title="Save changes"]').hidden = true;

function replaceMeetingDate() {
    const datepicker = document.querySelector('#new-meeting');
    const meeting_time = document.querySelector('#meeting-time');
    meeting_time.value = new Date(datepicker.value).toISOString();
    return true;
}