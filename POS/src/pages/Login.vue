<template>
  <div class="login-root">
    <!-- Background decorative orbs -->
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>

    <div class="login-wrapper">
      <!-- Brand header -->
      <div class="brand-header">
        <div class="brand-icon">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <path d="M20 7h-4V4c0-1.1-.9-2-2-2h-4c-1.1 0-2 .9-2 2v3H4c-1.1 0-2 .9-2 2v11c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V9c0-1.1-.9-2-2-2zM10 4h4v3h-4V4zm10 16H4V9h16v11z"/>
          </svg>
        </div>
        <h1 class="brand-title">One POS</h1>
        <p class="brand-subtitle">{{ __('Sign in to your point of sale system') }}</p>
      </div>

      <!-- Glass card -->
      <div class="glass-card">
        <!-- Error alert -->
        <div v-if="session.login.error" class="error-alert">
          <svg class="error-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
          <div>
            <p class="error-title">{{ __('Login Failed') }}</p>
            <p class="error-body">{{ session.login.error.messages.join('\n') }}</p>
          </div>
        </div>

        <form class="login-form" @submit.prevent="submit">
          <!-- Email field -->
          <div class="field-group">
            <label class="field-label">{{ __('User ID / Email') }}</label>
            <div class="input-wrapper">
              <span class="input-icon">
                <FeatherIcon name="user" class="h-4 w-4" :stroke-width="2" />
              </span>
              <input
                v-model="loginForm.email"
                required
                name="email"
                type="text"
                :placeholder="__('Enter your username or email')"
                :disabled="session.login.loading"
                class="login-input"
              />
            </div>
          </div>

          <!-- Password field -->
          <div class="field-group">
            <label class="field-label">{{ __('Password') }}</label>
            <div class="input-wrapper">
              <span class="input-icon">
                <FeatherIcon name="lock" class="h-4 w-4" :stroke-width="2" />
              </span>
              <input
                v-model="loginForm.password"
                required
                name="password"
                :type="showPassword ? 'text' : 'password'"
                :placeholder="__('Enter your password')"
                :disabled="session.login.loading"
                class="login-input"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="toggle-password"
                :disabled="session.login.loading"
                tabindex="-1"
                :aria-label="showPassword ? __('Hide password') : __('Show password')"
              >
                <FeatherIcon :name="showPassword ? 'eye-off' : 'eye'" class="h-4 w-4" :stroke-width="2" />
              </button>
            </div>
          </div>

          <!-- Submit button -->
          <button
            type="submit"
            class="submit-btn"
            :class="{ 'is-loading': session.login.loading }"
            :disabled="session.login.loading"
          >
            <span v-if="!session.login.loading" class="btn-content">
              <FeatherIcon name="log-in" class="h-4 w-4" :stroke-width="2.5" />
              {{ __('Sign in') }}
            </span>
            <span v-else class="btn-content">
              <svg class="spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
              {{ __('Signing in...') }}
            </span>
          </button>
        </form>
      </div>

      <p class="footer-note">© {{ new Date().getFullYear() }} One POS &mdash; Powered by ERPNext</p>
    </div>

    <!-- Shift Opening Dialog -->
    <ShiftOpeningDialog
      v-model="showShiftDialog"
      @shift-opened="handleShiftOpened"
      @dialog-closed="handleDialogClosed"
    />
  </div>
</template>

<script setup>
import { usePOSCartStore } from "@/stores/posCart"
import { usePOSUIStore } from "@/stores/posUI"
import { FeatherIcon } from "frappe-ui"
import { onMounted, reactive, ref, watch } from "vue"
import { useRouter } from "vue-router"
import ShiftOpeningDialog from "../components/ShiftOpeningDialog.vue"
import { useShift } from "../composables/useShift"
import { session } from "../data/session"
import { ensureCSRFToken } from "../utils/csrf"
import { offlineWorker } from "../utils/offline/workerClient"

const router = useRouter()
const { shiftState } = useShift()
const cartStore = usePOSCartStore()
const uiStore = usePOSUIStore()

const loginForm = reactive({
	email: "",
	password: "",
})

const showShiftDialog = ref(false)
const showPassword = ref(false)

// Reset state when login page mounts
onMounted(() => {
	// Clear login form
	loginForm.email = ""
	loginForm.password = ""
	showPassword.value = false

	// Clear any login errors
	if (session.login.error) {
		session.login.reset()
	}

	// Only clear state if user is NOT logged in
	// If user is already logged in (e.g., after successful login), don't clear their session
	if (!session.isLoggedIn) {
		showShiftDialog.value = false
		cartStore.clearCart()
		uiStore.resetAllDialogs()

		// Clear any stale shift state
		shiftState.value = {
			pos_opening_shift: null,
			pos_profile: null,
			company: null,
			isOpen: false,
		}
		localStorage.removeItem("pos_shift_data")
	}
})

function submit() {
	if (!loginForm.email || !loginForm.password) {
		return
	}

	session.login.submit({
		email: loginForm.email.trim(),
		password: loginForm.password,
	})
}

// Watch for successful login
watch(
	() => session.isLoggedIn,
	async (isLoggedIn) => {
		if (isLoggedIn) {
			// Initialize CSRF token after successful login
			try {
				console.log("User logged in, initializing CSRF token...")
				await ensureCSRFToken()

				// Sync CSRF token to worker for background API calls
				if (window.csrf_token) {
					await offlineWorker.setCSRFToken(window.csrf_token)
				}
			} catch (error) {
				console.error("Failed to initialize CSRF token after login:", error)
			}

			// Show shift opening dialog after successful login
			showShiftDialog.value = true
		}
	},
)

// Watch for dialog being closed via X button (v-model update)
// When user closes dialog without action, navigate to POSSale
watch(showShiftDialog, (isOpen, wasOpen) => {
	// Only navigate if dialog was open and is now closed, and user is logged in
	if (wasOpen === true && isOpen === false && session.isLoggedIn) {
		router.push({ name: "POSSale" })
	}
})

function handleShiftOpened() {
	// Navigate to POS sale after shift is opened
	router.push({ name: "POSSale" })
}

function handleDialogClosed({ reason }) {
	// Navigate to /pos when dialog is cancelled or resumed
	// "cancelled" means user closed dialog without action
	// "resumed" means user chose to resume existing shift
	// In both cases, navigate to POSSale (existing shift will be active)
	if (reason === "cancelled" || reason === "resumed") {
		router.push({ name: "POSSale" })
	}
}

// Clear error when user starts typing
watch([() => loginForm.email, () => loginForm.password], () => {
	if (session.login.error) {
		session.login.reset()
	}
})
</script>

<style scoped>
/* ── Root & background ─────────────────────────────────── */
.login-root {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  overflow: hidden;
  padding: 1.5rem;
  font-family: 'Inter', sans-serif;
}

/* ── Decorative orbs ───────────────────────────────────── */
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.35;
  animation: float 8s ease-in-out infinite;
  pointer-events: none;
}
.orb-1 {
  width: 380px;
  height: 380px;
  background: radial-gradient(circle, #6366f1, transparent);
  top: -80px;
  left: -80px;
  animation-delay: 0s;
}
.orb-2 {
  width: 320px;
  height: 320px;
  background: radial-gradient(circle, #8b5cf6, transparent);
  bottom: -60px;
  right: -60px;
  animation-delay: -3s;
}
.orb-3 {
  width: 240px;
  height: 240px;
  background: radial-gradient(circle, #06b6d4, transparent);
  top: 50%;
  right: 15%;
  animation-delay: -5s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) scale(1); }
  50%       { transform: translateY(-24px) scale(1.05); }
}

/* ── Wrapper ───────────────────────────────────────────── */
.login-wrapper {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.75rem;
  animation: slide-up 0.5s ease-out both;
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── Brand header ──────────────────────────────────────── */
.brand-header {
  text-align: center;
}
.brand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 18px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.5);
  margin-bottom: 1rem;
  color: #fff;
}
.brand-icon svg {
  width: 32px;
  height: 32px;
}
.brand-title {
  font-size: 2rem;
  font-weight: 800;
  color: #fff;
  letter-spacing: -0.5px;
  margin: 0 0 0.375rem;
}
.brand-subtitle {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.55);
  margin: 0;
}

/* ── Glass card ────────────────────────────────────────── */
.glass-card {
  width: 100%;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  padding: 2rem;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

/* ── Error alert ───────────────────────────────────────── */
.error-alert {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 10px;
  padding: 0.875rem 1rem;
  margin-bottom: 1.25rem;
}
.error-icon {
  flex-shrink: 0;
  width: 18px;
  height: 18px;
  color: #f87171;
  margin-top: 1px;
}
.error-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: #fca5a5;
  margin: 0 0 0.2rem;
}
.error-body {
  font-size: 0.8rem;
  color: rgba(252, 165, 165, 0.8);
  margin: 0;
}

/* ── Form ──────────────────────────────────────────────── */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* ── Field group ───────────────────────────────────────── */
.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.field-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  letter-spacing: 0.3px;
  text-transform: uppercase;
}

/* ── Input wrapper ─────────────────────────────────────── */
.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}
.input-icon {
  position: absolute;
  left: 0.875rem;
  color: rgba(255, 255, 255, 0.4);
  display: flex;
  align-items: center;
  pointer-events: none;
  transition: color 0.2s;
}
.login-input {
  width: 100%;
  padding: 0.75rem 2.75rem;
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.13);
  border-radius: 10px;
  color: #fff;
  font-size: 0.9rem;
  line-height: 1.5;
  outline: none;
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
  -webkit-appearance: none;
}
.login-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}
.login-input:focus {
  border-color: rgba(99, 102, 241, 0.7);
  background: rgba(99, 102, 241, 0.08);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}
.login-input:focus + .input-icon,
.input-wrapper:focus-within .input-icon {
  color: #818cf8;
}
.login-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.toggle-password {
  position: absolute;
  right: 0.875rem;
  display: flex;
  align-items: center;
  color: rgba(255, 255, 255, 0.4);
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  transition: color 0.2s;
}
.toggle-password:hover {
  color: rgba(255, 255, 255, 0.8);
}

/* ── Submit button ─────────────────────────────────────── */
.submit-btn {
  width: 100%;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1, #7c3aed);
  color: #fff;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.3px;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.45);
  transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s;
  margin-top: 0.25rem;
}
.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 28px rgba(99, 102, 241, 0.6);
}
.submit-btn:active:not(:disabled) {
  transform: scale(0.98);
  box-shadow: 0 2px 12px rgba(99, 102, 241, 0.4);
}
.submit-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

/* ── Spinner ───────────────────────────────────────────── */
.spin {
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

/* ── Footer ────────────────────────────────────────────── */
.footer-note {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.25);
  text-align: center;
  margin: 0;
}
</style>
