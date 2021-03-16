<template>
  <v-app>
      <v-tabs>
        <v-tab disabled>Design</v-tab>
        <v-tab>Test</v-tab>
        <v-tab-item>
        </v-tab-item>
        <v-tab-item>
          <TestIntent/>
        </v-tab-item>
      </v-tabs>
  </v-app>
</template>

<script>
import TestIntent from './components/TestIntent';

export default {
  name: 'App',

  components: {
    TestIntent,
  },

  data: () => ({
    //
  }),
};
</script>
