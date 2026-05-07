<template>
  <div>
    <v-card>
      <v-card-title class="d-flex align-center">
        <h2>{{ title }}</h2>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          icon="mdi-refresh"
          @click="handleRefresh"
          :loading="loading"
        ></v-btn>
      </v-card-title>
      
      <v-card-text>
        <v-alert
          v-if="error"
          type="error"
          class="mb-4"
        >
          {{ error }}
        </v-alert>
        
        <v-table>
          <thead>
            <tr>
              <th>{{ keyLabel }}</th>
              <th>{{ valueLabel }}</th>
              <th>{{ descriptionLabel }}</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="setting in settings" :key="setting.key">
              <td>{{ setting.key }}</td>
              <td>{{ setting.value }}</td>
              <td>{{ setting.description }}</td>
              <td>
                <v-btn
                  icon="mdi-pencil"
                  size="small"
                  variant="text"
                  @click="openEditDialog(setting)"
                ></v-btn>
              </td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
    </v-card>
    
    <!-- Edit Setting Dialog -->
    <v-dialog v-model="showEditDialog" max-width="500px">
      <v-card>
        <v-card-title>Edit {{ keyLabel }}: {{ currentSetting?.key }}</v-card-title>
        <v-card-text>
          <v-form ref="form" @submit.prevent="saveSetting">
            <v-text-field
              v-model="editedSetting.value"
              :label="valueLabel"
              :rules="[v => !!v || `${valueLabel} is required`]"
              required
            ></v-text-field>
            
            <v-textarea
              v-model="editedSetting.description"
              :label="descriptionLabel"
            ></v-textarea>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" @click="showEditDialog = false">Cancel</v-btn>
          <v-btn 
            color="primary" 
            @click="saveSetting"
            :loading="saving"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Setting {
  key: string;
  value: string;
  description: string | null;
  [key: string]: any;
}

interface SettingUpdate {
  value: string;
  description?: string;
  [key: string]: any;
}

const props = defineProps<{
  title: string;
  settings: ReadonlyArray<Setting> | Setting[];
  loading: boolean;
  error: string;
  keyLabel?: string;
  valueLabel?: string;
  descriptionLabel?: string;
}>();

const emit = defineEmits<{
  refresh: [];
  update: [key: string, data: SettingUpdate];
}>();

const showEditDialog = ref(false);
const currentSetting = ref<Setting | null>(null);
const editedSetting = ref<SettingUpdate>({
  value: '',
  description: ''
});
const saving = ref(false);
const form = ref<any>(null);

// Use provided labels or defaults
const keyLabel = props.keyLabel || 'Setting';
const valueLabel = props.valueLabel || 'Value';
const descriptionLabel = props.descriptionLabel || 'Description';

function handleRefresh() {
  emit('refresh');
}

function openEditDialog(setting: Setting) {
  currentSetting.value = setting;
  editedSetting.value = {
    value: setting.value,
    description: setting.description || ''
  };
  showEditDialog.value = true;
}

async function saveSetting() {
  if (!currentSetting.value) return;
  if (!form.value?.validate()) return;
  
  saving.value = true;
  
  try {
    emit('update', currentSetting.value.key, editedSetting.value);
    showEditDialog.value = false;
  } catch (err: any) {
    console.error('Failed to update setting', err);
  } finally {
    saving.value = false;
  }
}
</script> 