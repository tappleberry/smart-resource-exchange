// ==================================================
// CampusMart - Demand Intelligence Dashboard
// ==================================================


document.addEventListener("DOMContentLoaded", () => {

    const highDemandCount =
        document.getElementById(
            "high-demand-count"
        );

    const mediumDemandCount =
        document.getElementById(
            "medium-demand-count"
        );

    const lowDemandCount =
        document.getElementById(
            "low-demand-count"
        );

    const recommendedCount =
        document.getElementById(
            "recommended-count"
        );

    const recommendationResults =
        document.getElementById(
            "dashboard-recommendation-results"
        );

    const chartCanvas =
        document.getElementById(
            "demand-chart"
        );


    if (
        !highDemandCount ||
        !mediumDemandCount ||
        !lowDemandCount ||
        !recommendedCount ||
        !recommendationResults ||
        !chartCanvas
    ) {
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


    // --------------------------------------------------
    // Load dashboard data
    // --------------------------------------------------

    async function loadDashboard() {

        try {

            const demandResults = [];

            // ------------------------------------------
            // Get demand prediction for every category
            // ------------------------------------------

            for (
                const category
                of categories
            ) {

                const response =
                    await fetch(
                        `/api/demand/${encodeURIComponent(category)}/`
                    );

                const data =
                    await response.json();


                if (
                    response.ok &&
                    data.success
                ) {

                    demandResults.push(
                        data.result
                    );
                }
            }


            // ------------------------------------------
            // Count demand levels
            // ------------------------------------------

            let highCount = 0;
            let mediumCount = 0;
            let lowCount = 0;


            for (
                const result
                of demandResults
            ) {

                if (
                    result.demand_level
                    === "HIGH"
                ) {

                    highCount++;

                } else if (
                    result.demand_level
                    === "MEDIUM"
                ) {

                    mediumCount++;

                } else {

                    lowCount++;
                }
            }


            // ------------------------------------------
            // Update summary cards
            // ------------------------------------------

            highDemandCount.textContent =
                highCount;

            mediumDemandCount.textContent =
                mediumCount;

            lowDemandCount.textContent =
                lowCount;


            // ------------------------------------------
            // Get recommendations
            // ------------------------------------------

            const recommendationResponse =
                await fetch(
                    "/api/recommendations/"
                );

            const recommendationData =
                await recommendationResponse.json();


            let recommendations = [];


            if (
                recommendationResponse.ok &&
                recommendationData.success
            ) {

                recommendations =
                    recommendationData.recommendations;
            }


            // ------------------------------------------
            // Count recommended categories
            // ------------------------------------------

            const recommendedCategories =
                recommendations.filter(
                    (item) =>
                        item.recommended === true
                );


            recommendedCount.textContent =
                recommendedCategories.length;


            // ------------------------------------------
            // Create chart
            // ------------------------------------------

            const chartLabels =
                demandResults.map(
                    (result) =>
                        result.category
                );

            const chartScores =
                demandResults.map(
                    (result) =>
                        result.demand_score
                );


            new Chart(
                chartCanvas,
                {
                    type: "bar",

                    data: {
                        labels: chartLabels,

                        datasets: [
                            {
                                label:
                                    "Demand Score",

                                data:
                                    chartScores
                            }
                        ]
                    },

                    options: {
                        responsive: true,

                        maintainAspectRatio: false,

                        scales: {
                            y: {
                                beginAtZero: true,

                                max: 100
                            }
                        }
                    }
                }
            );


            // ------------------------------------------
            // Render recommendations
            // ------------------------------------------

            recommendationResults.innerHTML =
                "";


            if (
                recommendedCategories.length === 0
            ) {

                recommendationResults.innerHTML = `
                    <p>
                        No strong seller opportunities
                        right now.
                    </p>
                `;

                return;
            }


            for (
                const recommendation
                of recommendedCategories
            ) {

                const card =
                    document.createElement(
                        "div"
                    );

                card.className =
                    "recommendation-card";


                card.innerHTML = `
                    <h3>
                        ${recommendation.category}
                    </h3>

                    <p>
                        Demand Score:
                        <strong>
                            ${recommendation.demand_score}
                        </strong>
                    </p>

                    <p>
                        Recommendation:
                        <strong>
                            ${recommendation.recommendation_level}
                        </strong>
                    </p>

                    <p>
                        Listings:
                        ${recommendation.listings}
                    </p>

                    <p>
                        Exam Days:
                        ${recommendation.exam_days}
                    </p>

                    <p>
                        ${recommendation.message}
                    </p>
                `;


                recommendationResults.appendChild(
                    card
                );
            }


        } catch (error) {

            recommendationResults.innerHTML = `
                <p>
                    Unable to load dashboard data.
                </p>
            `;
        }
    }


    loadDashboard();

});