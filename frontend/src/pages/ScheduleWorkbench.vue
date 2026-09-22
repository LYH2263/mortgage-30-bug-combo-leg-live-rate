<script setup>
import { ref } from 'vue'
import { postJSON } from '../api'
const principal = ref(800000)
const annual_rate = ref(4.2)
const months = ref(360)
const out = ref(null)
const run = async () => { out.value = await postJSON('/api/schedule', { principal: principal.value, annual_rate: annual_rate.value, months: months.value, persist: true }) }

const commercial = ref({ principal: 600000, annual_rate: 3.6, months: 360 })
const fund = ref({ principal: 400000, annual_rate: 3.1, months: 240 })
const combo = ref(null)
const comboErr = ref('')
const runCombo = async () => {
  comboErr.value = ''
  try { combo.value = await postJSON('/api/combo/schedule', { commercial: commercial.value, fund: fund.value, persist: true, preview_rows: 12 }) }
  catch (e) { comboErr.value = `试算被拒：${e.message}` }
}
</script>
<template><div class="page"><h1>等额本息试算</h1>
<label>本金 <input v-model.number="principal" /></label>
<label>年利率% <input v-model.number="annual_rate" /></label>
<label>月数 <input v-model.number="months" /></label>
<button @click="run">计算</button>
<p v-if="out">月供 {{ out.monthly_payment }} · 利息合计 {{ out.total_interest }}</p>

<h1>组合贷试算（分腿与合并对照）</h1>
<fieldset><legend>商业贷款</legend>
<label>本金 <input v-model.number="commercial.principal" type="number" /></label>
<label>年利率% <input v-model.number="commercial.annual_rate" type="number" step="0.01" /></label>
<label>期数 <input v-model.number="commercial.months" type="number" /></label>
</fieldset>
<fieldset><legend>公积金贷款</legend>
<label>本金 <input v-model.number="fund.principal" type="number" /></label>
<label>年利率% <input v-model.number="fund.annual_rate" type="number" step="0.01" /></label>
<label>期数 <input v-model.number="fund.months" type="number" /></label>
</fieldset>
<button @click="runCombo">计算组合贷</button>
<p v-if="comboErr" class="err">{{ comboErr }}</p>
<div v-if="combo">
<table><tr><th></th><th>月供</th><th>利息合计</th><th>期数</th></tr>
<tr><td>商业腿</td><td>{{ combo.legs.commercial.monthly_payment }}</td><td>{{ combo.legs.commercial.total_interest }}</td><td>{{ combo.legs.commercial.months }}</td></tr>
<tr><td>公积金腿</td><td>{{ combo.legs.fund.monthly_payment }}</td><td>{{ combo.legs.fund.total_interest }}</td><td>{{ combo.legs.fund.months }}</td></tr>
<tr><td><b>合并</b></td><td><b>{{ combo.monthly_payment }}</b></td><td><b>{{ combo.total_interest }}</b></td><td>{{ combo.row_count }}</td></tr></table>
<table><tr><th>期</th><th>商业月供</th><th>公积金月供</th><th>合并月供</th><th>合并余额</th></tr>
<tr v-for="r in combo.preview" :key="r.period"><td>{{ r.period }}</td><td>{{ r.commercial_payment }}</td><td>{{ r.fund_payment }}</td><td>{{ r.payment }}</td><td>{{ r.balance }}</td></tr></table>
</div>
</div></template>
