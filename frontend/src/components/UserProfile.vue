<template>
  <div>
    <!-- Profile Header Section - Centered Layout -->
    <div class="text-center mb-6">
      <!-- Avatar -->
      <UserAvatar
        :image-url="editedProfile?.avatar_url"
        :name="editedProfile?.name"
        :size="96"
        editable
        @update:image-url="handleAvatarUpdate"
        class="mx-auto mb-2"
      />
      <!-- Name below avatar -->
      <h2 class="text-h6 font-weight-medium mt-2">{{ profileData.name || 'User' }}</h2>
      
      <!-- Credits display as a chip -->
      <v-chip
        color="primary"
        class="mt-2"
      >
        Contribution Index {{ credits ?? 0 }}
      </v-chip>
    </div>

    <v-list>
      <!-- <v-list-item>
        <v-list-item-title>Name</v-list-item-title>
        <v-list-item-subtitle>{{ profileData.name || 'Not set' }}</v-list-item-subtitle>
      </v-list-item> -->      
      <v-list-item>
        <v-list-item-title>Location</v-list-item-title>
        <v-list-item-subtitle>{{ profileData.location || 'Not set' }}</v-list-item-subtitle>
      </v-list-item>
      
      <v-list-item>
        <v-list-item-title>Workplace</v-list-item-title>
        <v-list-item-subtitle>{{ profileData.workplace || 'Not set' }}</v-list-item-subtitle>
      </v-list-item>

      <v-list-item>
        <v-list-item-title>Role</v-list-item-title>
        <v-list-item-subtitle>{{ profileData.role || 'Not set' }}</v-list-item-subtitle>
      </v-list-item>

      <v-list-item>
        <v-list-item-title>Birth Date</v-list-item-title>
        <v-list-item-subtitle>{{ profileData.birth_date || 'Not set' }}</v-list-item-subtitle>
      </v-list-item>
      
      <v-list-item>
        <v-list-item-title>Goals</v-list-item-title>
        <v-list-item-subtitle>{{ profileData.goals || 'Not set' }}</v-list-item-subtitle>
      </v-list-item>
      
      <v-list-item>
        <v-list-item-title>Education</v-list-item-title>
        <v-list-item-subtitle>{{ profileData.education || 'Not set' }}</v-list-item-subtitle>
      </v-list-item>
      
      <v-list-item v-if="!preview">
        <v-list-item-title>Referral Code</v-list-item-title>
        <v-list-item-subtitle class="d-flex align-center">
          {{ profileData.referral_code }}
          <v-btn
            icon="mdi-content-copy"
            size="small"
            variant="text"
            class="ms-2"
            @click="copyReferralCode"
          />
        </v-list-item-subtitle>
      </v-list-item>
      
      <v-list-item v-if="profileData.willing_to_contribute !== undefined">
        <v-list-item-title>Willing to Contribute</v-list-item-title>
        <v-list-item-subtitle>
          <v-icon
            :color="profileData.willing_to_contribute ? 'success' : 'error'"
            size="small"
            class="mr-1"
          >
            {{ profileData.willing_to_contribute ? 'mdi-check-circle' : 'mdi-close-circle' }}
          </v-icon>
          {{ profileData.willing_to_contribute ? 'Yes' : 'No' }}
        </v-list-item-subtitle>
      </v-list-item>
    </v-list>

    <!-- Edit Profile Button -->
    <div class="d-flex justify-end mt-4" v-if="!preview">
      <v-btn
        color="primary"
        prepend-icon="mdi-account-edit"
        @click="showEditDialog = true"
        variant="outlined"
      >
        Edit Profile
      </v-btn>
    </div>

    <!-- Edit Profile Dialog -->
    <v-dialog v-model="showEditDialog" max-width="600px">
      <v-card>
        <v-card-title>Edit Profile</v-card-title>
        <v-card-text>
          <v-form ref="form" @submit.prevent="handleSubmit">
            <v-text-field
              v-model="editedProfile.name"
              label="Name"
              :rules="[(v: string) => !!v || 'Name is required']"
            />
            
            <v-text-field
              v-model="editedProfile.location"
              label="Location"
            />

            <v-text-field
              v-model="editedProfile.workplace"
              label="Workplace"
            />

            <v-text-field
              v-model="editedProfile.role"
              label="Role"
            />

            <v-text-field
              v-model="editedProfile.birth_date"
              label="Birth Date"
              type="date"
            />

            <v-textarea
              v-model="editedProfile.goals"
              label="Goals"
            />

            <v-textarea
              v-model="editedProfile.education"
              label="Education"
            />
            
            <v-switch
              v-model="editedProfile.willing_to_contribute"
              label="Willing to contribute my knowledge"
              color="primary"
            />
          </v-form>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn color="error" @click="showEditDialog = false">Cancel</v-btn>
          <v-btn 
            color="primary" 
            @click="handleSubmit"
            :loading="isSubmitting"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
// @ts-ignore
import { ref, computed, nextTick } from 'vue'
import { updateProfile } from '@/stores/profile'
import { useStore } from 'effector-vue/composition'
import UserAvatar from './UserAvatar.vue'
import type { User, ProfileData } from '@/types'
import { $credits } from '@/stores/credits'

const props = defineProps<{
  profileData: ProfileData,
  preview?: boolean
}>()

const emit = defineEmits<{
  (e: 'update', data: Partial<ProfileData>): void
}>()

const credits = useStore($credits)

const showEditDialog = ref(false)
const isSubmitting = ref(false)
const form = ref<any>(null)

const editedProfile = ref({ ...props.profileData })


async function handleSubmit() {
  if (!form.value) return
  
  const { valid } = await form.value.validate()
  if (!valid) return

  isSubmitting.value = true
  try {
    // Update profile
    await updateProfile(editedProfile.value)
    emit('update', editedProfile.value)
    showEditDialog.value = false
  } catch (error) {
    console.error('Failed to update profile:', error)
  } finally {
    isSubmitting.value = false
  }
}

async function handleAvatarUpdate(avatarUrl: string) {
  console.log('Avatar updated:', avatarUrl)
  
  // Then set the new URL with timestamp to prevent caching
  const timestampedUrl = avatarUrl.includes('?t=') 
    ? avatarUrl  // Already has a timestamp
    : `${avatarUrl}?t=${Date.now()}` // Add timestamp
  
  editedProfile.value.avatar_url = timestampedUrl
  
  // Emit event with updated profile data including new avatar URL
  emit('update', { avatar_url: timestampedUrl })
}

async function copyReferralCode() {
  try {
    await navigator.clipboard.writeText(props.profileData.referral_code)
    // You might want to show a success notification here
  } catch (error) {
    console.error('Failed to copy referral code:', error)
  }
}
</script>
