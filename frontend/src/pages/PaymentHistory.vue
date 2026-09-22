<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const open = ref(null)
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
const toggle = (id) => { open.value = open.value === id ? null : id }
const kindLabel = (k) => k === 'combo_schedule' ? '组合贷' : '等额本息'
</script>
<template><div class="page"><h1>试算记录</h1>
<table><tr><th>#</th><th>类型</th><th>时间</th><th>月供</th><th></th></tr>
<template v-for="h in items" :key="h.id">
<tr><td>#{{ h.id }}</td><td>{{ kindLabel(h.kind) }}</td><td>{{ h.created_at }}</td>
<td>{{ h.result?.monthly_payment }}</td>
<td><a href="#" @click.prevent="toggle(h.id)">{{ open === h.id ? '收起' : '打开' }}</a></td></tr>
<tr v-if="open === h.id"><td colspan="5">
<template v-if="h.kind === 'combo_schedule'">
<p>商业月供 <b>{{ h.result.legs.commercial.monthly_payment }}</b>（{{ h.input.commercial.principal }} 元 · {{ h.input.commercial.annual_rate }}% · {{ h.input.commercial.months }} 期）</p>
<p>公积金月供 <b>{{ h.result.legs.fund.monthly_payment }}</b>（{{ h.input.fund.principal }} 元 · {{ h.input.fund.annual_rate }}% · {{ h.input.fund.months }} 期）</p>
<p>合并月供 <b>{{ h.result.monthly_payment }}</b> · 利息合计 {{ h.result.total_interest }}</p>
</template>
<template v-else>
<p>月供 <b>{{ h.result.monthly_payment }}</b> · 利息合计 {{ h.result.total_interest }}</p>
<p v-if="h.input">本金 {{ h.input.principal }} 元 · {{ h.input.annual_rate }}% · {{ h.input.months }} 期</p>
</template>
</td></tr>
</template></table>
</div></template>
