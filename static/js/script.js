document
    .getElementById("signup-form")
    .addEventListener("submit", async (e) => {
        e.preventDefault();

        const name = document.getElementById("name").value.trim();
        const email = document.getElementById("email").value.trim();
        const phone = document.getElementById("phone").value.trim();
        const referralCode = document
            .getElementById("referralCode")
            .value.trim();

        // Check for empty fields
        if (!name || !email || !phone) {
            document.getElementById("result").innerHTML =
                "Error: All fields except referral code are required.";
            return;
        }

        const response = await fetch("/signup", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ name, email, phone, referralCode }),
        });
        const result = await response.json();
        if (result.error) {
            document.getElementById(
                "result"
            ).innerHTML = `Error: ${result.error}`;
        } else {
            document.getElementById(
                "result"
            ).innerHTML = `Your position in the waitlist: ${result.position}<br>Your referral code: ${result.referralCode}`;
            document.getElementById("signup-result").style.display = "block";
            document.getElementById("position").textContent = result.position;
            document.getElementById("referral-code").textContent =
                result.referralCode;
        }
    });

document.addEventListener("DOMContentLoaded", function () {
    fetch("/rank-data")
        .then((response) => {
            if (!response.ok) {
                throw new Error("Failed to fetch rankings");
            }
            return response.json();
        })
        .then((data) => {
            const rankTable = document.getElementById("rank-table-body");
            rankTable.innerHTML = ""; // Clear existing rows

            if (data.length === 0) {
                const row = document.createElement("tr");
                row.innerHTML = `
                <td colspan="5" style="text-align: center;">No rankings available</td> <!-- Updated colspan -->
              `;
                rankTable.appendChild(row);
            } else {
                data.forEach((customer) => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                  <td>${customer.position}</td>
                  <td>${customer.name}</td>
                  <td>${customer.email}</td>
                  <td>${customer.referral_code}</td>
                  <td>${customer.referred_persons || 0
                        }</td> <!-- Display referred persons or default to 0 -->
                `;
                    rankTable.appendChild(row);
                });
            }
        })
        .catch((error) => {
            console.error("Error fetching rankings:", error);
            const rankTable = document.getElementById("rank-table-body");
            rankTable.innerHTML = `
              <tr>
                <td colspan="5" style="text-align: center; color: red;">Error loading rankings</td> <!-- Updated colspan -->
              </tr>
            `;
        });
});