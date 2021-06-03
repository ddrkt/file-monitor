export default class {
    apiHost = 'http://localhost:5000'

    constructor(container = '#app', params = {}, callback = () => {}) {
        this.params = params;
        this._renderContainer = document.querySelector(container);
        this._callback = callback;

        this.listeners = new Map();
        this.onceListeners = new Map();
        this.triggerdLabels = new Map()
        this.initialize();
    }

    initialize() {
    }

    getApiHost() {
        return this.apiHost
    }

    async makeRequest(endpoint, method, data) {
        const response =  await fetch(`${this.getApiHost()}/${endpoint}`, {
            method: method,
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'token_key': this.params.token
            },
            body: JSON.stringify(data)
        });
        return [await response.json(), response.status]
    }

    getErrorView(error) {
        return `
            <p class="error-message">Error occurred: <b>${error}</b></p>
        `;
    }

    async getView() {
        return ``;
    }

    onRender() {
    }

    queryElement(selector) {
        return this._renderContainer.querySelector(selector)
    }

    async _renderView() {
        this._renderContainer.innerHTML = await this.getView();
    }

    async render() {
        await this._renderView();
        this.onRender();
        this._callback();
    }

    // help-function for onReady and onceReady
    // the callbackfunction will execute,
    // if the label has already been triggerd with the last called parameters
    _fCheckPast(label, callback) {
        if (this.triggerdLabels.has(label)) {
            callback(this.triggerdLabels.get(label));
            return true;
        } else {
            return false;
        }
    }

    // execute the callback everytime the label is trigger
    on(label, callback, checkPast = false) {
        this.listeners.has(label) || this.listeners.set(label, []);
        this.listeners.get(label).push(callback);
        if (checkPast) {
            this._fCheckPast(label, callback);
        }
    }

    // execute the callback everytime the label is trigger
    // check if the label had been already called
    // and if so excute the callback immediately
    onReady(label, callback) {
        this.on(label, callback, true);
    }

    // execute the callback onetime the label is trigger
    once(label, callback, checkPast = false) {
        this.onceListeners.has(label) || this.onceListeners.set(label, []);
        if (!(checkPast && this._fCheckPast(label, callback))) {
            // label wurde nocht nicht aufgerufen und
            // der callback in _fCheckPast nicht ausgeführt
            this.onceListeners.get(label).push(callback);
        }
    }

    // execute the callback onetime the label is trigger
    // or execute the callback if the label had been called already
    onceReady(label, callback) {
        this.once(label, callback, true);
    }

    // remove the callback for a label
    off(label, callback = true) {
        if (callback === true) {
            // remove listeners for all callbackfunctions
            this.listeners.delete(label);
            this.onceListeners.delete(label);
        } else {
            // remove listeners only with match callbackfunctions
            let _off = (inListener) => {
                let listeners = inListener.get(label);
                if (listeners) {
                    inListener.set(label, listeners.filter((value) => !(value === callback)));
                }
            };
            _off(this.listeners);
            _off(this.onceListeners);
        }
    }

    // trigger the event with the label
    trigger(label, ...args) {
        let res = false;
        this.triggerdLabels.set(label, ...args); // save all triggerd labels for onready and onceready
        let _trigger = (inListener, label, ...args) => {
            let listeners = inListener.get(label);
            if (listeners && listeners.length) {
                listeners.forEach((listener) => {
                    listener(...args);
                });
                res = true;
            }
        };
        _trigger(this.onceListeners, label, ...args);
        _trigger(this.listeners, label, ...args);
        this.onceListeners.delete(label); // callback for once executed, so delete it.
        return res;
    }
}
