<template>
  <div class="container" style="width: 50%;">
    <select v-model="ticker" @change="fetchTicker">
      <option v-for="ticker in tickers" :value="ticker">
        {{ ticker }}
      </option>
    </select>
    <Line v-if="loaded" :chart-data="mutchartData" :chart-options="options" />
  </div>
</template>

<script>
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  LineElement,
  PointElement,
  TimeSeriesScale,
} from 'chart.js'

ChartJS.register(TimeSeriesScale,
  Title, Tooltip,
  Legend, CategoryScale, LinearScale, LineElement, PointElement)

export default {
  name: 'App',
  components: { Line },
  data: () => ({
    loaded: false,
    ticker: 'ticker_00',
    tickers: ['ticker_00'],
    chartData: {
      labels: [],
      datasets: [{
        label: 'ticker_00',
        data: [],
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
        borderJoinStyle: 'round',
        cubicInterpolationMode: 'monotone',
        stepped: true,
        pointRadius: 2,
        clip: 3
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            suggestedMin: 0,
          },
          stacked: true
        },
      }
    },
    autofetch: null,
    end_ts: null,
    start_ts: null,
  }),
  methods: {
    async fetchTicker() {
      if (this.autofetch) {
        clearInterval(this.autofetch);
      }
      const resp = await fetch(`/api/ticker/v1/state/${this.ticker}`);
      const { prices, timestamps } = await resp.json();
      this.start_ts = timestamps[0];
      this.end_ts = timestamps[timestamps.length - 1];
      this.chartData.labels = timestamps.map((item) => item - this.start_ts);
      this.chartData.datasets[0].data = prices;
      this.chartData.datasets[0].label = this.ticker;

      this.autofetch = setInterval(() => {
        this.fetchNew().then(({ prices, timestamps }) => {
          if (timestamps.length == 0) return;
          this.end_ts = timestamps[timestamps.length - 1];
          this.chartData.labels.push(...timestamps.map((item) => item - this.start_ts));
          this.chartData.datasets[0].data.push(...prices);
        })
      }, 1000)
    },
    async fetchNew() {
      const resp = await fetch(`/api/ticker/v1/state/${this.ticker}?left=${this.end_ts + 1}`);
      const { prices, timestamps } = await resp.json();
      return { prices, timestamps }
    },
    async fetchTickers() {
      const resp = await fetch('/api/ticker/v1/list');
      this.tickers = await resp.json();
    }
  },
  async mounted() {
    this.loaded = false

    try {
      this.fetchTickers();
      await this.fetchTicker();
      this.loaded = true
    } catch (e) {
      console.error(e)
    }
  },
  computed: {
    mutchartData() {
      return this.chartData;
    }
  },

}
</script>
