<template>
  <v-app>
      <v-tabs v-model="activeTab">
        <v-tab>Design</v-tab>
        <v-tab
            :disabled="this.intents.length === 0"
        >Test</v-tab>
        <v-tab-item>
          <DesignIntent
              v-bind="{
                openapi: this.openapi,
                intents: this.intents,
              }"/>
        </v-tab-item>
        <v-tab-item>
          <TestIntent
              v-bind="{
                openapi: this.openapi,
                intents: this.intents,
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
  }),

  created: function() {
    this.init();
  },

  methods: {
    init() {
      this.getAPIDescription();
      this.getIntents();
    },
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
  }
};
</script>
