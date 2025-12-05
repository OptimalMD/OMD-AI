<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { WEBUI_API_BASE_URL, WEBUI_BASE_URL } from '$lib/constants';
	import { WEBUI_NAME, user, config, socket } from '$lib/stores';
	import { getBackendConfig } from '$lib/apis';
	import Spinner from '$lib/components/common/Spinner.svelte';

	const i18n = getContext('i18n');

	let loaded = false;
	let name = '';
	let email = '';
	let agreementChecked = false;

	const guestSignInHandler = async () => {
		if (!name || !email) {
			toast.error('Please enter your name and email');
			return;
		}

		if (!agreementChecked) {
			toast.error('Please acknowledge the disclaimer');
			return;
		}

		// Basic email validation
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		if (!emailRegex.test(email)) {
			toast.error('Please enter a valid email address');
			return;
		}

		const loadingToast = toast.loading('Creating guest session...');

		try {
			const res = await fetch(`${WEBUI_API_BASE_URL}/auths/guest`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					name,
					email
				})
			});

			if (!res.ok) {
				const error = await res.json();
				throw new Error(error.detail || 'Failed to create guest session');
			}

			const sessionData = await res.json();
			
			toast.dismiss(loadingToast);
			
			if (sessionData.token) {
				// Store token with session storage (will clear on browser close)
				sessionStorage.setItem('token', sessionData.token);
				sessionStorage.setItem('guest_mode', 'true');
				
				// Set in localStorage for the user store to pick up
				localStorage.token = sessionData.token;
				
				// Emit socket user-join event if socket is available
				if ($socket) {
					$socket.emit('user-join', { auth: { token: sessionData.token } });
				}
				
				// Set the user in the store (auto-login)
				await user.set(sessionData);
				
				// Update config
				await config.set(await getBackendConfig());
				
				toast.success(`Welcome ${sessionData.name}! You are now in guest mode.`);
				
				// Redirect to main app
				const redirectPath = $page.url.searchParams.get('redirect') || '/';
				goto(redirectPath);
			} else {
				toast.error('Failed to create guest session');
			}
		} catch (error) {
			toast.dismiss(loadingToast);
			toast.error(`${error}`);
		}
	};

	const submitHandler = async (e: Event) => {
		e.preventDefault();
		await guestSignInHandler();
	};

	onMount(async () => {
		const redirectPath = $page.url.searchParams.get('redirect');
		if ($user !== undefined) {
			goto(redirectPath || '/');
		}

		loaded = true;
	});
</script>

<svelte:head>
	<title>Guest Access - {$WEBUI_NAME}</title>
</svelte:head>

<div class="w-full h-screen max-h-[100dvh] text-white relative" id="guest-page">
	<div class="w-full h-full absolute top-0 left-0 bg-white dark:bg-gray-950"></div>

	<div class="w-full absolute top-0 left-0 right-0 h-8 drag-region"></div>

	{#if loaded}
		<div
			class="fixed inset-0 bg-transparent w-full h-full flex font-primary z-50 text-black dark:text-white overflow-y-auto"
			id="guest-container"
		>
			<div class="w-full min-h-full flex flex-col lg:flex-row">
				<!-- Left Side - Branding -->
				<div class="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900 dark:to-gray-800 p-12 flex-col justify-center items-center">
					<div class="max-w-xl text-center">
						<!-- Logo -->
						<div class="mb-8 flex justify-center">
							<img
								crossorigin="anonymous"
								src="{WEBUI_BASE_URL}/static/favicon.png"
								class="h-16 w-16 rounded-full"
								alt="OptimalMD Logo"
							/>
						</div>
						
						<!-- Main Heading -->
						<h1 class="text-4xl font-bold text-gray-900 dark:text-white mb-4">
							Try My AI Doctor™
						</h1>
						
						<!-- Subheading -->
						<p class="text-xl text-gray-600 dark:text-gray-300 mb-6">
							Test our AI-powered health companion without signing up
						</p>

						<!-- Features -->
						<div class="text-left space-y-4">
							<div class="flex items-start">
								<svg class="w-6 h-6 text-blue-600 dark:text-blue-400 mr-3 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
								</svg>
								<div>
									<h3 class="font-semibold text-gray-900 dark:text-white">No signup required</h3>
									<p class="text-sm text-gray-600 dark:text-gray-400">Just enter your name and email to get started</p>
								</div>
							</div>

							<div class="flex items-start">
								<svg class="w-6 h-6 text-blue-600 dark:text-blue-400 mr-3 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
								</svg>
								<div>
									<h3 class="font-semibold text-gray-900 dark:text-white">Session expires on close</h3>
									<p class="text-sm text-gray-600 dark:text-gray-400">Your session automatically ends when you close the browser</p>
								</div>
							</div>

							<div class="flex items-start">
								<svg class="w-6 h-6 text-blue-600 dark:text-blue-400 mr-3 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
								</svg>
								<div>
									<h3 class="font-semibold text-gray-900 dark:text-white">Full features access</h3>
									<p class="text-sm text-gray-600 dark:text-gray-400">Experience all features available to test the platform</p>
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Right Side - Form -->
				<div class="w-full lg:w-1/2 flex items-center justify-center px-6 py-10 lg:px-12">
					<div class="w-full max-w-md dark:text-gray-100">
						<!-- Mobile Logo -->
						<div class="lg:hidden flex justify-center mb-8">
							<img
								crossorigin="anonymous"
								src="{WEBUI_BASE_URL}/static/favicon.png"
								class="h-16 w-16 rounded-full"
								alt="OptimalMD Logo"
							/>
						</div>

						<!-- Mobile Title -->
						<div class="lg:hidden mb-8 text-center">
							<h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
								Guest Access
							</h1>
							<p class="text-sm text-gray-600 dark:text-gray-400">
								Try our platform without signing up
							</p>
						</div>

						<!-- Form -->
						<form class="flex flex-col" on:submit={submitHandler}>
							<!-- Form Title -->
							<div class="mb-6">
								<h2 class="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white">
									Start Your Guest Session
								</h2>
								<p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
									Enter your details to access the platform as a guest
								</p>
							</div>

							<div class="flex flex-col space-y-4">
								<div>
									<label for="name" class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
										Full Name <span class="text-red-500">*</span>
									</label>
									<input
										bind:value={name}
										type="text"
										id="name"
										class="w-full px-4 py-3 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
										placeholder="Enter your full name"
										required
									/>
								</div>

								<div>
									<label for="email" class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
										Email Address <span class="text-red-500">*</span>
									</label>
									<input
										bind:value={email}
										type="email"
										id="email"
										class="w-full px-4 py-3 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
										placeholder="Enter your email address"
										required
									/>
									<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
										We'll never share your email with anyone else.
									</p>
								</div>

								<!-- Disclaimer -->
								<div class="flex items-start space-x-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
									<input
										type="checkbox"
										id="agreement"
										bind:checked={agreementChecked}
										class="mt-1 h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500"
									/>
									<label for="agreement" class="text-xs text-gray-700 dark:text-gray-300">
										By entering this site, you fully acknowledge this is not medical advice and not intended to replace
										the relationship with your physician. OptimalMD accepts no responsibility for actions taken based on
										the information gained from this AI diagnostic tool. It is for educational and research use only.
									</label>
								</div>
							</div>

							<div class="mt-6">
								<button
									class="w-full bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition duration-200 ease-in-out transform hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
									type="submit"
								>
									Continue as Guest
								</button>

								<!-- Links to Auth -->
								<div class="mt-6 text-sm text-center text-gray-600 dark:text-gray-400">
									Already have an account?
									<a
										href="/auth"
										class="font-semibold text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 ml-1 transition"
									>
										Sign in
									</a>
								</div>

								<div class="mt-2 text-sm text-center text-gray-600 dark:text-gray-400">
									Want to create an account?
									<a
										href="/auth?form=signup"
										class="font-semibold text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 ml-1 transition"
									>
										Sign up
									</a>
								</div>
							</div>
						</form>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	#guest-page {
		background: white;
	}

	:global(.dark) #guest-page {
		background: rgb(3 7 18);
	}

	#guest-container {
		transition: background-color 0.3s ease;
	}

	#guest-container::-webkit-scrollbar {
		width: 8px;
	}

	#guest-container::-webkit-scrollbar-track {
		background: transparent;
	}

	#guest-container::-webkit-scrollbar-thumb {
		background: rgba(156, 163, 175, 0.3);
		border-radius: 4px;
	}

	:global(.dark) #guest-container::-webkit-scrollbar-thumb {
		background: rgba(75, 85, 99, 0.5);
	}
</style>
