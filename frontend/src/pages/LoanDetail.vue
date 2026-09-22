<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON, postJSON, putJSON } from '../api'
const route = useRoute()
const loan = ref(null)
const sch = ref(null)
const legs = ref(null)
const combo = ref(null)
const msg = ref('')
const err = ref('')
const blankLegs = (p) => ({
  commercial: { principal: Math.round(p * 0.6), annual_rate: 3.6, months: 360 },
  fund: { principal: Math.round(p * 0.4), annual_rate: 3.1, months: 240 },
})
const previewCombo = async () => {
  combo.value = await postJSON('/api/combo/schedule', { ...legs.value, loan_id: loan.value.id, persist: false, preview_rows: 12 })
}
const load = async () => {
  msg.value = ''; err.value = ''; combo.value = null; sch.value = null
  loan.value = await getJSON(`/api/loans/${route.params.id}`)
  if (loan.value.legs) {
    legs.value = JSON.parse(JSON.stringify(loan.value.legs))
    await previewCombo()
  } else {
    legs.value = null
    sch.value = await postJSON('/api/schedule', { principal: loan.value.principal, annual_rate: loan.value.annual_rate, months: loan.value.months, loan_id: loan.value.id, persist: false, preview_rows: 6 })
  }
}
const enableCombo = () => { legs.value = blankLegs(loan.value.principal); msg.value = ''; err.value = '' }
const saveLegs = async () => {
  err.value = ''; msg.value = ''
  try {
    loan.value = await putJSON(`/api/loans/${loan.value.id}/legs`, legs.value)
    legs.value = JSON.parse(JSON.stringify(loan.value.legs))
    msg.value = '两腿已保存'
    await previewCombo()
  } catch (e) { err.value = `保存被拒：${e.message}` }
}
const tryCombo = async () => {
  err.value = ''
  try { await previewCombo() } catch (e) { err.value = `试算被拒：${e.message}` }
}
onMounted(load); watch(() => route.params.id, load)
</script>
<template><div class="page" v-if="loan"><h1>{{ loan.name }}</h1>
<p v-if="err" class="err">{{ err }}</p><p v-if="msg">{{ msg }}</p>

<template v-if="legs">
<h2>组合贷 · 两腿</h2>
<fieldset><legend>商业贷款</legend>
<label>本金 <input v-model.number="legs.commercial.principal" type="number" /></label>
<label>年利率% <input v-model.number="legs.commercial.annual_rate" type="number" step="0.01" /></label>
<label>期数 <input v-model.number="legs.commercial.months" type="number" /></label>
</fieldset>
<fieldset><legend>公积金贷款</legend>
<label>本金 <input v-model.number="legs.fund.principal" type="number" /></label>
<label>年利率% <input v-model.number="legs.fund.annual_rate" type="number" step="0.01" /></label>
<label>期数 <input v-model.number="legs.fund.months" type="number" /></label>
</fieldset>
<button @click="saveLegs">保存两腿</button> <button @click="tryCombo">试算</button>

<div v-if="combo">
<p>商业月供 <b>{{ combo.legs.commercial.monthly_payment }}</b> · 公积金月供 <b>{{ combo.legs.fund.monthly_payment }}</b></p>
<p>合并月供 <span class="hero-num">{{ combo.monthly_payment }}</span> · 利息合计 {{ combo.total_interest }}</p>
<table><tr><th>期</th><th>商业月供</th><th>公积金月供</th><th>合并月供</th><th>利息</th><th>余额</th></tr>
<tr v-for="r in combo.preview" :key="r.period"><td>{{ r.period }}</td><td>{{ r.commercial_payment }}</td><td>{{ r.fund_payment }}</td><td>{{ r.payment }}</td><td>{{ r.interest }}</td><td>{{ r.balance }}</td></tr></table>
</div>
</template>

<template v-else>
<p>月供 <span class="hero-num">{{ sch?.monthly_payment }}</span></p>
<table><tr v-for="r in sch?.preview" :key="r.period"><td>{{ r.period }}</td><td>{{ r.payment }}</td><td>{{ r.principal }}</td><td>{{ r.interest }}</td></tr></table>
<p><button @click="enableCombo">挂载组合贷（商业+公积金两腿）</button></p>
</template>
</div></template>
