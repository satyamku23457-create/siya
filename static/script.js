document.addEventListener("DOMContentLoaded", function () {

    const yesBtn = document.getElementById("yesBtn");
    const noBtn = document.getElementById("noBtn");
    const hint = document.getElementById("hint");
    const success = document.getElementById("success");

    if (!yesBtn || !noBtn || !hint || !success) {
        console.error("Page 1 elements missing.");
        return;
    }

    const messages = [
        "Please ek baar aur soch lo 🥺",
        "Please, sach mein ek baar aur ❤️",
        "Itni jaldi NO mat bolo 🥹",
        "Please ek chance aur de do ❤️",
        "Ek baar dil se soch lo 🥺",
        "Pleaseeeee ❤️",
        "Bas ek baar dil se YES try kar lo 🥹",
        "Please ❤️"
    ];

    let noCount = 0;
    let busy = false;

    const maxNoClicks = 8;


    // =========================
    // SEND RESPONSE
    // =========================

    function saveResponse(answer) {

        fetch("/response", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                answer: answer,
                noClicks: noCount
            }),
            keepalive: true
        })
        .then(response => {

            if (!response.ok) {
                throw new Error("Server error");
            }

            return response.json();

        })
        .then(data => {

            console.log(
                `${answer} response saved:`,
                data
            );

        })
        .catch(error => {

            console.error(
                `${answer} response error:`,
                error
            );

        });
    }


    // =========================
    // YES
    // =========================

    yesBtn.addEventListener("click", function () {

        if (busy) return;

        busy = true;

        // UI changes IMMEDIATELY
        success.classList.add("show");

        // Send in background.
        // UI does not wait for email.
        saveResponse("YES");

    });


    // =========================
    // NO
    // =========================

    noBtn.addEventListener("click", function () {

        if (busy) return;

        noCount++;

        const index = Math.min(
            noCount - 1,
            messages.length - 1
        );

        let message = messages[index];

        const remaining = Math.max(
            maxNoClicks - noCount,
            0
        );

        if (remaining > 0) {

            message +=
                `\n\nNO ke ${remaining} chances bache hain ❤️`;

        } else {

            message +=
                "\n\nAb tumhara final decision hai ❤️";

        }

        hint.innerText = message;


        // =========================
        // YES BIGGER
        // =========================

        const yesScale = Math.min(
            1 + (noCount * 0.10),
            1.8
        );

        yesBtn.style.transform =
            `scale(${yesScale})`;


        // =========================
        // NO SMALLER + MOVE
        // =========================

        const noScale = Math.max(
            1 - (noCount * 0.07),
            0.55
        );

        const moveX =
            Math.floor(Math.random() * 100) - 50;

        const moveY =
            Math.floor(Math.random() * 60) - 30;

        noBtn.style.transform =
            `translate(${moveX}px, ${moveY}px) scale(${noScale})`;


        // =========================
        // SAVE NO
        // =========================

        saveResponse("NO");

    });

});