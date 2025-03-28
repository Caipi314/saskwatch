async function getData() {
	el = document.querySelector('#data');
	const url = "/data";
	try {
		const response = await fetch(url);
		if (!response.ok) {
			throw new Error(`Response status: ${response.status}`);
		}

		const json = await response.json();
		const str = JSON.stringify(json, null, 2);
		el.innerHTML = str;
	} catch (error) {
		console.error(error.message);
	}
}

getData()
int = setInterval(getData, 1000);
window.addEventListener('beforeunload', () => clearInterval(int));