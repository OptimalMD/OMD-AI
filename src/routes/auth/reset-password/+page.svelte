<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { toast } from 'svelte-sonner';
	import { resetPassword } from '$lib/apis/auths';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import SensitiveInput from '$lib/components/common/SensitiveInput.svelte';

	let token = '';
	let newPassword = '';
	let confirmPassword = '';
	let loading = false;
	let success = false;

	onMount(() => {
		token = $page.url.searchParams.get('token') || '';
		if (!token) {
			toast.error('Invalid reset link');
			goto('/auth');
		}
	});

	const handleResetPassword = async () => {
		if (!newPassword || newPassword.length < 8) {
			toast.error('Password must be at least 8 characters long');
			return;
		}

		if (newPassword !== confirmPassword) {
			toast.error('Passwords do not match');
			return;
		}

		loading = true;

		try {
			const result = await resetPassword(token, newPassword);
			
			if (result && result.success) {
				success = true;
				toast.success('Password reset successful! Redirecting to login...');
				setTimeout(() => {
					goto('/auth');
				}, 2000);
			} else {
				toast.error('Failed to reset password. Please try again.');
			}
		} catch (error) {
			const errorMessage = error?.toString() || 'An error occurred. Please request a new reset link.';
			toast.error(errorMessage);
		} finally {
			loading = false;
		}
	};
</script>

<div id="reset-password-page" class="min-h-screen flex items-center justify-center p-4">
	<div class="w-full max-w-md">
		<div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl overflow-hidden">
			<!-- Header -->
			<div class="bg-gradient-to-r from-green-600 to-green-700 p-8 text-white text-center">
				<h1 class="text-3xl font-bold">Reset Your Password</h1>
				<p class="text-green-100 mt-2">Enter your new password below</p>
			</div>

			<!-- Content -->
			<div class="p-8">
				{#if success}
					<div class="text-center">
						<div class="text-6xl mb-4">✓</div>
						<h2 class="text-2xl font-bold text-green-600 dark:text-green-400 mb-2">
							Success!
						</h2>
						<p class="text-gray-600 dark:text-gray-300">
							Your password has been reset successfully.
						</p>
						<p class="text-sm text-gray-500 dark:text-gray-400 mt-2">
							Redirecting to login...
						</p>
					</div>
				{:else if loading}
					<div class="flex flex-col items-center justify-center py-8">
						<Spinner className="w-8 h-8 text-green-600" />
						<p class="mt-4 text-gray-600 dark:text-gray-300">Resetting your password...</p>
					</div>
				{:else}
					<form on:submit|preventDefault={handleResetPassword}>
						<div class="mb-6">
							<label 
								for="new-password" 
								class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block"
							>
								New Password
							</label>
							<SensitiveInput
								bind:value={newPassword}
								type="password"
								id="new-password"
								inputClassName="w-full px-4 py-3 pr-12 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition"
								showButtonClassName="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition"
								placeholder="Enter your new password"
								required
								autocomplete="new-password"
							/>
							<p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
								Minimum 8 characters
							</p>
						</div>

						<div class="mb-6">
							<label 
								for="confirm-password" 
								class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block"
							>
								Confirm New Password
							</label>
							<SensitiveInput
								bind:value={confirmPassword}
								type="password"
								id="confirm-password"
								inputClassName="w-full px-4 py-3 pr-12 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition"
								showButtonClassName="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition"
								placeholder="Confirm your new password"
								required
								autocomplete="new-password"
							/>
						</div>

						<button
							type="submit"
							class="w-full px-4 py-3 text-sm font-medium text-white bg-gradient-to-r from-green-600 to-green-700 rounded-lg hover:from-green-700 hover:to-green-800 focus:outline-none focus:ring-2 focus:ring-green-500 transition shadow-md hover:shadow-lg"
						>
							Reset Password
						</button>

						<div class="mt-6 text-center">
							<a 
								href="/auth" 
								class="text-sm text-gray-600 dark:text-gray-400 hover:text-green-600 dark:hover:text-green-400 transition"
							>
								← Back to Login
							</a>
						</div>
					</form>
				{/if}
			</div>
		</div>
	</div>
</div>

<style>
	#reset-password-page {
		background: white;
	}

	:global(.dark) #reset-password-page {
		background: rgb(3 7 18);
	}
</style>
