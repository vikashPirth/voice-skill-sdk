<template>
  <v-app>
      <v-tabs
          v-model="activeTab"
          icons-and-text
      >
        <v-tab>
          Design
          <v-icon>mdi-developer-board</v-icon>
        </v-tab>
        <v-tab
            :disabled="this.intents.length === 0"
        >Test
          <v-icon>mdi-view-dashboard</v-icon>
        </v-tab>
        <v-tab-item>
          <DesignIntent
              v-bind="{
                openapi: this.openapi,
                intents: this.intents,
                log: this.log,
              }"/>
        </v-tab-item>
        <v-tab-item>
          <TestIntent
              v-bind="{
                openapi: this.openapi,
                intents: this.intents,
                log: this.log,
              }"/>
        </v-tab-item>
      </v-tabs>
  </v-app>
</template>

<script>

import DesignIntent from './components/DesignIntent';
import TestIntent from './components/TestIntent';

export default {
  name: 'App',

  components: {
    DesignIntent,
    TestIntent,
  },

  data: () => ({
    openapi: {},
    intents: [],
    activeTab: 0,
    log: "",
    connection: null,
  }),

  created: function() {
    this.getAPIDescription();
    this.getIntents();
    this.connectLogs();
  },

  methods: {
    getIntents() {
      const uri = 'http://localhost:4242/intents'
      this.axios.get(uri).then(
          r => {
            this.intents = r.data;
            this.activeTab = r.data.length > 0 ? 1 : 0;
          }
      )
    },
    getAPIDescription() {
      const uri = 'http://localhost:4242/openapi.json'
      this.axios.get(uri).then(
          r => this.openapi = r.data
      )
    },
    connectLogs() {

      this.connection = new WebSocket("ws://localhost:4242/logs");

      const self = this
      this.connection.onmessage = function(event) {
        const container = document.getElementById ( "log" )
        container.scrollTop = container.scrollHeight
        self.log += JSON.parse(event.data).msg + "\n"
      }

      this.connection.onopen = function(event) {
        console.log(event)
        console.log("Successfully connected to the logs server...")
      }
    },
  }
};
</script>
