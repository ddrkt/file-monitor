import AbstractView from './abstractView.js';

export default class extends AbstractView {
    initialize() {
        this.status = false;
        this.validToken = '';
    }

    getView() {
        return `
            <div class="input-group">
                <label for="token-input">Token</label>
                <input id="token-input" name="token-input" value="${this.getToken()}" type="text">
            </div>
            <button class="btn" id="verify">Verify token</button>
            <p class="auth-status">Status: 
                <b class="${this.status ? 'status-active' : 'status-inactive'}">
                    ${this.status ? 'Active' : 'Inactive'}
                </b>
            </p>
        `;
    }

    async verifyToken() {
        this.queryElement('#verify').classList.add('btn-load')
        const [data, status] = await this.makeRequest('verify_token', 'POST');
        if (status === 200 && data.token_valid) {
            this.validToken = this.params.token;
            this.status = true;
        } else {
            this.validToken = '';
            this.status = false;
        }
        await this.render();
        this.trigger('tokenChange', this.status)
    }

    getToken() {
        return this.validToken;
    }

    onRender() {
        this.queryElement('#token-input').addEventListener('change', e => {
            this.params.token = e.target.value;
        });
        this.queryElement('#verify').addEventListener('click', async () => { await this.verifyToken() });
    }
}
