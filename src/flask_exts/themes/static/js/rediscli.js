const KEY_UP = 38;
const KEY_DOWN = 40;
const MAX_ITEMS = 128;

class History {
	constructor() {
		this.items = [];
		this.position = 0;
	}

	add(cmd) {
		this.items.push(cmd);
		if (this.items.length > MAX_ITEMS) {
			this.items.shift();
		}
		this.position = this.items.length;
	}

	getPrevious() {
		if (this.position > 0) {
			this.position -= 1;
		}
		return this.items[this.position] || '';
	}

	getNext() {
		if (this.position < this.items.length) {
			this.position += 1;
		}
		return this.items[this.position] || '';
	}
}

class RedisCli {
	constructor() {
		this.history = new History();
		this.console = document.querySelector('.console');
		this.container = this.console.querySelector('.console-container');
		this.form = this.console.querySelector('form');
		this.postUrl = this.form.getAttribute('action');
		this.input = this.form.querySelector('input');

		// Bind methods
		this.resizeConsole = this.resizeConsole.bind(this);
		this.submitCommand = this.submitCommand.bind(this);
		this.onKeyPress = this.onKeyPress.bind(this);

		this.form.addEventListener('submit', this.submitCommand);
		this.input.addEventListener('keydown', this.onKeyPress);
		window.addEventListener('resize', this.resizeConsole);
	}

	resizeConsole() {
		const height = window.innerHeight;
		const offset = this.console.getBoundingClientRect();
		this.console.style.height = `${height - offset.top}px`;
	}

	scrollBottom = () => {
		this.container.scrollTo({
			top: this.container.scrollHeight,
			behavior: 'smooth'
		});
	}

	createElementWithClass(tagName, className, content, isHtml = true) {
		const elem = document.createElement(tagName);
		const classNames = className.split(' ');
		classNames.forEach(c => elem.classList.add(c));
		if (isHtml) {
			elem.innerHTML = content;
		} else {
			elem.textContent = content;
		}
		return elem;
	}

	createEntry(cmd) {
		const entry = document.createElement('div');
		entry.classList.add('entry');

		const cmdElement = document.createElement('div');
		cmdElement.className = 'cmd';
		cmdElement.textContent = cmd;

		entry.appendChild(cmdElement);

		this.container.appendChild(entry);


		if (this.container.children.length > MAX_ITEMS)
			this.container.removeChild(this.container.firstChild);

		this.scrollBottom();
		return entry;
	}

	sendCommand(val) {
		let entry = this.createEntry('> ' + val);
		this.history.add(val);
		fetch(this.postUrl,
			{
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ 'cmd': val }),
			})
			.then(response => response.text())
			.then(data => {
				const responseDiv = this.createElementWithClass('div', 'response', data);
				entry.appendChild(responseDiv);
			})
			.catch(() => {
				const responseDiv = this.createElementWithClass('div', 'response error', 'Failed to communicate with server.');
				entry.appendChild(responseDiv);
			})
			.finally(() => {
				this.scrollBottom();
			});
	}

	submitCommand(event) {
		event.preventDefault();
		// const postUrl = event.target.getAttribute('action');
		const formData = new FormData(event.target);
		const cmd = formData.get('cmd').trim();
		if (cmd.length) {
			this.sendCommand(cmd);
			this.input.value = '';
		}
	}

	onKeyPress(event) {
		if (event.keyCode == KEY_UP) {
			this.input.value = this.history.getPrevious();
		} else if (event.keyCode == KEY_DOWN) {
			this.input.value = this.history.getNext();
		}
	}
}

