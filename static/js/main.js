// ==================================================
// CampusMart - Main JavaScript
// Demand Intelligence + Recommendations
// ==================================================


document.addEventListener("DOMContentLoaded", () => {

    // --------------------------------------------------
    // Demand section
    // --------------------------------------------------

    const demandResults =
        document.getElementById("demand-results");


    if (!demandResults) {
        return;
    }


    // --------------------------------------------------
    // Categories
    // --------------------------------------------------

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
    // Create Demand Card
    // --------------------------------------------------

    function createDemandCard(result) {

        const card =
            document.createElement("div");

        card.className = "demand-card";


        card.innerHTML = `
            <h3>
                ${result.category}
            </h3>

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


        return card;
    }


    // --------------------------------------------------
    // Load Demand Data
    // --------------------------------------------------

    async function loadDemand() {

        demandResults.innerHTML = "";


        for (const category of categories) {

            const loadingCard =
                document.createElement("div");

            loadingCard.className =
                "demand-card";


            loadingCard.innerHTML = `
                <h3>
                    ${category}
                </h3>

                <p>
                    Loading...
                </p>
            `;


            demandResults.appendChild(
                loadingCard
            );


            try {

                const response =
                    await fetch(
                        `/api/demand/${encodeURIComponent(category)}/`
                    );


                const data =
                    await response.json();


                if (
                    !response.ok ||
                    !data.success
                ) {

                    loadingCard.innerHTML = `
                        <h3>
                            ${category}
                        </h3>

                        <p>
                            Demand data unavailable
                        </p>
                    `;

                    continue;
                }


                const card =
                    createDemandCard(
                        data.result
                    );


                loadingCard.replaceWith(
                    card
                );


            } catch (error) {

                loadingCard.innerHTML = `
                    <h3>
                        ${category}
                    </h3>

                    <p>
                        Unable to load demand data
                    </p>
                `;
            }
        }
    }


    // ==================================================
    // Recommendation Section
    // ==================================================

    function createRecommendationSection() {

        const section =
            document.createElement("section");

        section.id =
            "recommendation-section";


        section.innerHTML = `
            <h2>
                Seller Recommendations
            </h2>

            <div id="recommendation-results">
                <p>
                    Loading recommendations...
                </p>
            </div>
        `;


        demandResults.parentElement.insertAdjacentElement(
            "afterend",
            section
        );


        return document.getElementById(
            "recommendation-results"
        );
    }


    // --------------------------------------------------
    // Create Recommendation Card
    // --------------------------------------------------

    function createRecommendationCard(
        recommendation
    ) {

        const card =
            document.createElement("div");

        card.className =
            "recommendation-card";


        const recommendedText =
            recommendation.recommended
                ? "Recommended"
                : "Not Recommended";


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
                Status:
                <strong>
                    ${recommendedText}
                </strong>
            </p>

            <p>
                ${recommendation.message}
            </p>
        `;


        return card;
    }


    // --------------------------------------------------
    // Load Recommendations
    // --------------------------------------------------

    async function loadRecommendations(
        recommendationResults
    ) {

        try {

            const response =
                await fetch(
                    "/api/recommendations/"
                );


            const data =
                await response.json();


            if (
                !response.ok ||
                !data.success
            ) {

                recommendationResults.innerHTML = `
                    <p>
                        Recommendations unavailable.
                    </p>
                `;

                return;
            }


            recommendationResults.innerHTML =
                "";


            if (
                !data.recommendations ||
                data.recommendations.length === 0
            ) {

                recommendationResults.innerHTML = `
                    <p>
                        No recommendations available.
                    </p>
                `;

                return;
            }


            for (
                const recommendation
                of data.recommendations
            ) {

                const card =
                    createRecommendationCard(
                        recommendation
                    );


                recommendationResults.appendChild(
                    card
                );
            }


        } catch (error) {

            recommendationResults.innerHTML = `
                <p>
                    Unable to load recommendations.
                </p>
            `;
        }
    }


    // --------------------------------------------------
    // Initialize Recommendation Section
    // --------------------------------------------------

    const recommendationResults =
        createRecommendationSection();


    // --------------------------------------------------
    // Load everything
    // --------------------------------------------------

    loadDemand();

    loadRecommendations(
        recommendationResults
    );

});