document.addEventListener("DOMContentLoaded", () => {

    const demandResults =
        document.getElementById("demand-results");

    if (!demandResults) {
        return;
    }

    const categories = [
        "Electronics",
        "Books",
        "Cycles",
        "Hostel Essentials",
        "Lab Equipment",
        "Furniture",
        "Clothing",
        "Sports Equipment"
    ];

    async function loadDemand() {

        demandResults.innerHTML = "";

        for (const category of categories) {

            const card =
                document.createElement("div");

            card.className = "demand-card";

            card.innerHTML = `
                <h3>${category}</h3>
                <p>Loading...</p>
            `;

            demandResults.appendChild(card);

            try {

                const response = await fetch(
                    `/api/demand/${encodeURIComponent(category)}/`
                );

                const data =
                    await response.json();

                if (!response.ok || !data.success) {

                    card.innerHTML = `
                        <h3>${category}</h3>
                        <p>Demand data unavailable</p>
                    `;

                    continue;
                }

                const result =
                    data.result;

                card.innerHTML = `
                    <h3>${result.category}</h3>

                    <p>
                        Demand Score:
                        <strong>
                            ${result.demand_score}
                        </strong>
                    </p>

                    <p>
                        Demand Level:
                        <strong>
                            ${result.demand_level}
                        </strong>
                    </p>

                    <p>
                        Searches:
                        ${result.features.searches}
                    </p>

                    <p>
                        Views:
                        ${result.features.views}
                    </p>

                    <p>
                        Favorites:
                        ${result.features.favorites}
                    </p>

                    <p>
                        Listings:
                        ${result.features.listings}
                    </p>

                `;

            } catch (error) {

                card.innerHTML = `
                    <h3>${category}</h3>
                    <p>Unable to load demand data</p>
                `;
            }
        }
    }

    loadDemand();

});