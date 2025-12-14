<script lang="ts">
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';
	import { createEventDispatcher } from 'svelte';
	import { onMount, getContext } from 'svelte';

	import { goto } from '$app/navigation';

	import { updateUserById, getUserGroupsById } from '$lib/apis/users';

	import Modal from '$lib/components/common/Modal.svelte';
	import localizedFormat from 'dayjs/plugin/localizedFormat';
	import XMark from '$lib/components/icons/XMark.svelte';
	import SensitiveInput from '$lib/components/common/SensitiveInput.svelte';
	import UserProfileImage from '$lib/components/chat/Settings/Account/UserProfileImage.svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();
	dayjs.extend(localizedFormat);

	export let show = false;
	export let selectedUser;
	export let sessionUser;

	$: if (show) {
		init();
	}

	const init = () => {
		if (selectedUser) {
			_user = selectedUser;
			_user.password = '';
			loadUserGroups();
		}
	};

	let _user = {
		profile_image_url: '',
		role: 'pending',
		name: '',
		email: '',
		password: ''
	};

	let userGroups: any[] | null = null;

	const submitHandler = async () => {
		const res = await updateUserById(localStorage.token, selectedUser.id, _user).catch((error) => {
			toast.error(`${error}`);
		});

		if (res) {
			dispatch('save');
			show = false;
		}
	};

	const loadUserGroups = async () => {
		if (!selectedUser?.id) return;
		userGroups = null;

		userGroups = await getUserGroupsById(localStorage.token, selectedUser.id).catch((error) => {
			toast.error(`${error}`);
			return null;
		});
	};
</script>

<Modal size="sm" bind:show>
	<div>
		<div class=" flex justify-between dark:text-gray-300 px-5 pt-4 pb-2">
			<div class=" text-lg font-medium self-center">{$i18n.t('Edit User')}</div>
			<button
				class="self-center"
				on:click={() => {
					show = false;
				}}
			>
				<XMark className={'size-5'} />
			</button>
		</div>

		<div class="flex flex-col md:flex-row w-full md:space-x-4 dark:text-gray-200">
			<div class=" flex flex-col w-full sm:flex-row sm:justify-center sm:space-x-6">
				<form
					class="flex flex-col w-full"
					on:submit|preventDefault={() => {
						submitHandler();
					}}
				>
					<div class="px-5 pt-3 pb-5 w-full">
						<!-- Profile Image Section -->
						<div class="flex flex-col items-center pb-4 border-b border-gray-200 dark:border-gray-700 mb-4">
							<UserProfileImage
								imageClassName="size-16"
								bind:profileImageUrl={_user.profile_image_url}
								user={_user}
							/>
							<div class="text-center mt-3">
								<div class="font-semibold text-base capitalize truncate">
									{selectedUser.name}
								</div>
								<div class="text-xs text-gray-500 mt-1">
									{$i18n.t('Created at')}
									{dayjs(selectedUser.created_at * 1000).format('LL')}
								</div>
							</div>
						</div>

						<!-- User Groups Section -->
						{#if (userGroups ?? []).length > 0}
							<div class="mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
								<div class="mb-2 text-xs font-medium text-gray-700 dark:text-gray-300">
									{$i18n.t('User Groups')}
								</div>
								<div class="flex flex-wrap gap-2">
									{#each userGroups as userGroup}
										<span
											class="px-2.5 py-1 rounded-lg bg-gray-100 dark:bg-gray-800 text-xs font-medium hover:bg-gray-200 dark:hover:bg-gray-700 transition cursor-pointer"
										>
											<a
												href={'/admin/users/groups?id=' + userGroup.id}
												on:click|preventDefault={() =>
													goto('/admin/users/groups?id=' + userGroup.id)}
											>
												{userGroup.name}
											</a>
										</span>
									{/each}
								</div>
							</div>
						{/if}

						<!-- Form Fields -->
						<div class="flex flex-col space-y-4">
							<!-- Role -->
							<div class="flex flex-col">
								<label class="mb-1.5 text-xs font-medium text-gray-700 dark:text-gray-300">
									{$i18n.t('Role')}
								</label>
								<select
									class="w-full px-3 py-2 text-sm bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600"
									bind:value={_user.role}
									disabled={_user.id == sessionUser.id}
									required
								>
									<option value="admin">{$i18n.t('Admin')}</option>
									<option value="user">{$i18n.t('User')}</option>
									<option value="pending">{$i18n.t('Pending')}</option>
								</select>
							</div>

							<!-- Name -->
							<div class="flex flex-col">
								<label class="mb-1.5 text-xs font-medium text-gray-700 dark:text-gray-300">
									{$i18n.t('Name')}
								</label>
								<input
									class="w-full px-3 py-2 text-sm bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600"
									type="text"
									bind:value={_user.name}
									placeholder={$i18n.t('Enter Your Name')}
									autocomplete="off"
									required
								/>
							</div>

							<!-- Email -->
							<div class="flex flex-col">
								<label class="mb-1.5 text-xs font-medium text-gray-700 dark:text-gray-300">
									{$i18n.t('Email')}
								</label>
								<input
									class="w-full px-3 py-2 text-sm bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600"
									type="email"
									bind:value={_user.email}
									placeholder={$i18n.t('Enter Your Email')}
									autocomplete="off"
									required
								/>
							</div>

							<!-- OAuth ID (if exists) -->
							{#if _user?.oauth_sub}
								<div class="flex flex-col">
									<label class="mb-1.5 text-xs font-medium text-gray-700 dark:text-gray-300">
										{$i18n.t('OAuth ID')}
									</label>
									<div class="px-3 py-2 text-sm bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg break-all">
										{_user.oauth_sub ?? ''}
									</div>
								</div>
							{/if}

							<!-- New Password -->
							<div class="flex flex-col">
								<label class="mb-1.5 text-xs font-medium text-gray-700 dark:text-gray-300">
									{$i18n.t('New Password')}
								</label>
								<div class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg focus-within:ring-2 focus-within:ring-blue-500 dark:focus-within:ring-blue-600">
									<SensitiveInput
										outerClassName="flex flex-1"
										inputClassName="w-full text-sm bg-transparent outline-none"
										showButtonClassName="pl-1.5 transition bg-transparent"
										type="password"
										placeholder={$i18n.t('Enter New Password')}
										bind:value={_user.password}
										autocomplete="new-password"
										required={false}
									/>
								</div>
							</div>
						</div>

						<!-- Save Button -->
						<div class="flex justify-end pt-5 mt-4 border-t border-gray-200 dark:border-gray-700">
							<button
								class="px-5 py-2.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-lg shadow-sm"
								type="submit"
							>
								{$i18n.t('Save')}
							</button>
						</div>
					</div>
				</form>
			</div>
		</div>
	</div>
</Modal>

<style>
	input::-webkit-outer-spin-button,
	input::-webkit-inner-spin-button {
		/* display: none; <- Crashes Chrome on hover */
		-webkit-appearance: none;
		margin: 0; /* <-- Apparently some margin are still there even though it's hidden */
	}

	.tabs::-webkit-scrollbar {
		display: none; /* for Chrome, Safari and Opera */
	}

	.tabs {
		-ms-overflow-style: none; /* IE and Edge */
		scrollbar-width: none; /* Firefox */
	}

	input[type='number'] {
		-moz-appearance: textfield; /* Firefox */
	}
</style>
