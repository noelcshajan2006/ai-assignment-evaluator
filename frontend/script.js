async function submitAssignment() {

    try {
        const content = document.getElementById("assignment").value;

        if (!content || content.trim() === "") {
            alert("Please enter assignment content");
            return;
        }

        const response = await fetch("http://127.0.0.1:8000/evaluate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                content: content
            })
        });

        const data = await response.json();

        document.getElementById("result").innerText =
            "📊 Score: " + data.score +
            "\n\n🧠 AI Output:\n" + data.result;

    } catch (error) {
        console.error(error);
        document.getElementById("result").innerText =
            "Error connecting to backend";
    }
}