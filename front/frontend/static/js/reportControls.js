import AbstractView from './abstractView.js';

export default class extends AbstractView {
    initialize() {
        this.active = false;
        this.periodKey = 'days';
        this.periodVal = 1;
    }

    setActiveState(state = true) {
        this.active = state;
        this.render();
    }

    showValidationErrors(val) {
        this.queryElement('#errors').innerText = `Incorrect period value. Should be above 0, got ${val}`;
    }

    clearValidationErrors() {
        this.queryElement('#errors').innerText = '';
    }

    validatePeriodVal(val) {
        if (val <= 0) {
            this.showValidationErrors(val);
            return false;
        }
        this.clearValidationErrors();
        return true;
    }

    getPeriod() {
        const period = {};
        period[this.periodKey] = this.periodVal;
        return period;
    }

    setLoadState(state) {
        if (state) {
            this.queryElement('#getreport').classList.add('btn-load');
        } else {
            this.queryElement('#getreport').classList.remove('btn-load');
        }
    }

    onRender() {
        this.queryElement('#period-key').addEventListener('change', e => {
           this.periodKey = e.target.value;
        });
        this.queryElement('#period-val').addEventListener('change', e => {
            const val = e.target.value;
            const valid = this.validatePeriodVal(val);
            this.periodVal = val;
        });
        this.queryElement('#getreport').addEventListener('click', () => {
            const valid = this.validatePeriodVal(this.periodVal);
            if (valid) {
                this.setLoadState(true);
                this.trigger('getReport', this.getPeriod());
            }
        })
    }

    getView() {
        return `
            <p><b>Report period:</b></p>
            <p class="errors" id="errors"></p>
            <div class="input-group">
                <select id="period-key" name="period-key">
                    <option value="days" ${this.periodKey === 'days' ? 'selected' : ''}>Days</option>
                    <option value="hours" ${this.periodKey === 'hours' ? 'selected' : ''}>Hours</option>
                </select>
                <input type="number" id="period-val" name="period-val" value="${this.periodVal}">
            </div>
            <button class="btn" id="getreport" ${this.active ? '' : 'disabled'}>Get report</button>
        `;
    }
}
