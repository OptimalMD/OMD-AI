<script lang="ts">
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { updateUserPassword } from '$lib/apis/auths';
	import SensitiveInput from '$lib/components/common/SensitiveInput.svelte';

	const i18n = getContext('i18n');

	let currentPassword = '';
	let newPassword = '';
	let newPasswordConfirm = '';

	const updatePasswordHandler = async () => {
		if (newPassword === newPasswordConfirm) {
			const res = await updateUserPassword(localStorage.token, currentPassword, newPassword).catch(
				(error) => {
					toast.error(`${error}`);
					return null;
				}
			);

			if (res) {
				toast.success($i18n.t('Successfully updated.'));
			}

			currentPassword = '';
			newPassword = '';
			newPasswordConfirm = '';
		} else {
			toast.error(
				$i18n.t("The passwords you entered don't quite match. Please double-check and try again.")
			);
			newPassword = '';
			newPasswordConfirm = '';
		}
	};
</script>

<form
	class="flex flex-col text-sm"
	on:submit|preventDefault={() => {
		updatePasswordHandler();
	}}
>
	<div class="space-y-4">
		<div class="flex flex-col w-full">
			<div class="mb-2 text-xs font-medium text-gray-600 dark:text-gray-400">
				{$i18n.t('Current Password')}
			</div>

			<div class="flex-1">
				<SensitiveInput
					outerClassName="flex flex-1 w-full px-4 py-2.5 text-sm bg-gray-50 dark:bg-gray-900 dark:text-gray-300 rounded-lg border border-gray-200 dark:border-gray-700 focus-within:border-gray-400 dark:focus-within:border-gray-600 transition"
					inputClassName="w-full text-sm bg-transparent outline-none"
					showButtonClassName="pl-2 transition bg-transparent"
					type="password"
					bind:value={currentPassword}
					placeholder={$i18n.t('Enter your current password')}
					autocomplete="current-password"
					required
				/>
			</div>
		</div>

		<div class="flex flex-col w-full">
			<div class="mb-2 text-xs font-medium text-gray-600 dark:text-gray-400">
				{$i18n.t('New Password')}
			</div>

			<div class="flex-1">
				<SensitiveInput
					outerClassName="flex flex-1 w-full px-4 py-2.5 text-sm bg-gray-50 dark:bg-gray-900 dark:text-gray-300 rounded-lg border border-gray-200 dark:border-gray-700 focus-within:border-gray-400 dark:focus-within:border-gray-600 transition"
					inputClassName="w-full text-sm bg-transparent outline-none"
					showButtonClassName="pl-2 transition bg-transparent"
					type="password"
					bind:value={newPassword}
					placeholder={$i18n.t('Enter your new password')}
					autocomplete="new-password"
					required
				/>
			</div>
		</div>

		<div class="flex flex-col w-full">
			<div class="mb-2 text-xs font-medium text-gray-600 dark:text-gray-400">
				{$i18n.t('Confirm Password')}
			</div>

			<div class="flex-1">
				<SensitiveInput
					outerClassName="flex flex-1 w-full px-4 py-2.5 text-sm bg-gray-50 dark:bg-gray-900 dark:text-gray-300 rounded-lg border border-gray-200 dark:border-gray-700 focus-within:border-gray-400 dark:focus-within:border-gray-600 transition"
					inputClassName="w-full text-sm bg-transparent outline-none"
					showButtonClassName="pl-2 transition bg-transparent"
					type="password"
					bind:value={newPasswordConfirm}
					placeholder={$i18n.t('Confirm your new password')}
					autocomplete="off"
					required
				/>
			</div>
		</div>
	</div>

	<div class="mt-4 flex justify-end">
		<button
			class="px-4 py-2.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-lg"
		>
			{$i18n.t('Update password')}
		</button>
	</div>
</form>
