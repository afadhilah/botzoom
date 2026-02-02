<script setup lang="ts">
import type { HTMLAttributes } from "vue"
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
} from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { useSignup } from '@/features/auth/composables'

const props = defineProps<{
  class?: HTMLAttributes["class"]
}>()

// Auth logic
const { formData, isLoading, error, successMessage, handleSignup } = useSignup()
</script>

<template>
  <div :class="cn('flex flex-col gap-6', props.class)">
    <Card>
      <CardHeader class="text-center">
        <CardTitle class="text-xl">
          Create your account
        </CardTitle>
        <CardDescription>
          Enter your email below to create your account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit.prevent="handleSignup">
          <FieldGroup>
            <!-- Error message -->
            <div v-if="error" class="bg-destructive/15 text-destructive text-sm p-3 rounded-md mb-4">
              {{ error }}
            </div>
            
            <!-- Success message -->
            <div v-if="successMessage" class="bg-green-500/15 text-green-700 text-sm p-3 rounded-md mb-4">
              {{ successMessage }}
            </div>
            
            <Field>
              <FieldLabel for="name">
                Full Name
              </FieldLabel>
              <Input id="name" v-model="formData.full_name" type="text" placeholder="John Doe" required />
            </Field>
            <Field>
              <FieldLabel for="email">
                Email
              </FieldLabel>
              <Input
                id="email"
                v-model="formData.email"
                type="email"
                placeholder="m@example.com"
                required
              />
            </Field>
            <Field>
              <Field class="grid grid-cols-2 gap-4">
                <Field>
                  <FieldLabel for="password">
                    Password
                  </FieldLabel>
                  <Input id="password" v-model="formData.password" type="password" minlength="8" required />
                </Field>
                <Field>
                  <FieldLabel for="confirm-password">
                    Confirm Password
                  </FieldLabel>
                  <Input id="confirm-password" type="password" required />
                </Field>
              </Field>
              <FieldDescription>
                Must be at least 8 characters long.
              </FieldDescription>
            </Field>
            <Field>
              <Button type="submit" :disabled="isLoading">
                {{ isLoading ? 'Creating account...' : 'Create Account' }}
              </Button>
              <FieldDescription class="text-center">
                Already have an account? <a href="/auth/login">Sign in</a>
              </FieldDescription>
            </Field>
          </FieldGroup>
        </form>
      </CardContent>
    </Card>
    <FieldDescription class="px-6 text-center">
      By clicking continue, you agree to our <a href="#">Terms of Service</a>
      and <a href="#">Privacy Policy</a>.
    </FieldDescription>
  </div>
</template>
