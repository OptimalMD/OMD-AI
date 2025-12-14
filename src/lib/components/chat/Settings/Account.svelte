<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { onMount, getContext } from 'svelte';

	import { user, config, settings } from '$lib/stores';
	import { updateUserProfile, createAPIKey, getAPIKey, getSessionUser } from '$lib/apis/auths';
	import { WEBUI_BASE_URL } from '$lib/constants';

	import UpdatePassword from './Account/UpdatePassword.svelte';
	import { getGravatarUrl } from '$lib/apis/utils';
	import { generateInitialsImage, canvasPixelTest } from '$lib/utils';
	import { copyToClipboard } from '$lib/utils';
	import Plus from '$lib/components/icons/Plus.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import SensitiveInput from '$lib/components/common/SensitiveInput.svelte';
	import Textarea from '$lib/components/common/Textarea.svelte';
	import { getUserById } from '$lib/apis/users';
	import User from '$lib/components/icons/User.svelte';
	import UserProfileImage from './Account/UserProfileImage.svelte';
	import { getUserOrganization } from '$lib/apis/organizations';

	const i18n = getContext('i18n');

	export let saveHandler: Function;
	export let saveSettings: Function;

	let loaded = false;

	let profileImageUrl = '';
	let name = '';
	let bio = '';

	let _gender = '';
	let gender = '';
	let dateOfBirth = '';

	let webhookUrl = '';
	let showAPIKeys = false;

	let JWTTokenCopied = false;

	let APIKey = '';
	let APIKeyCopied = false;
	let profileImageInputElement: HTMLInputElement;

	// Organization data
	let userOrganization = null;

	// Active tab
	let activeTab = 'personal';

	const submitHandler = async () => {
		if (name !== $user?.name) {
			if (profileImageUrl === generateInitialsImage($user?.name) || profileImageUrl === '') {
				profileImageUrl = generateInitialsImage(name);
			}
		}

		if (webhookUrl !== $settings?.notifications?.webhook_url) {
			saveSettings({
				notifications: {
					...$settings.notifications,
					webhook_url: webhookUrl
				}
			});
		}

		const updatedUser = await updateUserProfile(localStorage.token, {
			name: name,
			profile_image_url: profileImageUrl,
			bio: bio ? bio : null,
			gender: gender ? gender : null,
			date_of_birth: dateOfBirth ? dateOfBirth : null
		}).catch((error) => {
			toast.error(`${error}`);
		});

		if (updatedUser) {
			// Get Session User Info
			const sessionUser = await getSessionUser(localStorage.token).catch((error) => {
				toast.error(`${error}`);
				return null;
			});

			await user.set(sessionUser);
			return true;
		}
		return false;
	};

	const createAPIKeyHandler = async () => {
		APIKey = await createAPIKey(localStorage.token);
		if (APIKey) {
			toast.success($i18n.t('API Key created.'));
		} else {
			toast.error($i18n.t('Failed to create API Key.'));
		}
	};

	onMount(async () => {
		const user = await getSessionUser(localStorage.token).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (user) {
			name = user?.name ?? '';
			profileImageUrl = user?.profile_image_url ?? '';
			bio = user?.bio ?? '';

			_gender = user?.gender ?? '';
			gender = _gender;

			dateOfBirth = user?.date_of_birth ?? '';
		}

		webhookUrl = $settings?.notifications?.webhook_url ?? '';

		APIKey = await getAPIKey(localStorage.token).catch((error) => {
			console.log(error);
			return '';
		});

		// Load user's organization if they have one
		try {
			userOrganization = await getUserOrganization(localStorage.token);
		} catch (error) {
			console.log('No organization found for user:', error);
		}

		loaded = true;
	});
</script>

<div id="tab-account" class="flex flex-col h-full text-sm">
	<!-- Tab Navigation -->
	{#if ($config?.features.enable_login_form && $user?.user_type !== 'guest' && $user?.user_type !== 'omd') || (($config?.features?.enable_api_key ?? true) || $user?.role === 'admin') && $user?.user_type !== 'guest' && $user?.user_type !== 'omd'}
		<div class="flex gap-2 mb-4 border-b border-gray-200 dark:border-gray-700">
			<button
				class="px-4 py-2.5 font-medium transition relative {activeTab === 'personal'
					? 'text-gray-900 dark:text-white'
					: 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'}"
				on:click={() => (activeTab = 'personal')}
			>
				{$i18n.t('Personal')}
				{#if activeTab === 'personal'}
					<div class="absolute bottom-0 left-0 right-0 h-0.5 bg-gray-900 dark:bg-white"></div>
				{/if}
			</button>
			{#if $config?.features.enable_login_form && $user?.user_type !== 'guest' && $user?.user_type !== 'omd'}
				<button
					class="px-4 py-2.5 font-medium transition relative {activeTab === 'password'
						? 'text-gray-900 dark:text-white'
						: 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'}"
					on:click={() => (activeTab = 'password')}
				>
					{$i18n.t('Change Password')}
					{#if activeTab === 'password'}
						<div class="absolute bottom-0 left-0 right-0 h-0.5 bg-gray-900 dark:bg-white"></div>
					{/if}
				</button>
			{/if}
			{#if (($config?.features?.enable_api_key ?? true) || $user?.role === 'admin') && $user?.user_type !== 'guest' && $user?.user_type !== 'omd'}
				<button
					class="px-4 py-2.5 font-medium transition relative {activeTab === 'api'
						? 'text-gray-900 dark:text-white'
						: 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'}"
					on:click={() => (activeTab = 'api')}
				>
					{$i18n.t('API')}
					{#if activeTab === 'api'}
						<div class="absolute bottom-0 left-0 right-0 h-0.5 bg-gray-900 dark:bg-white"></div>
					{/if}
				</button>
			{/if}
		</div>
	{/if}

	<div class="flex-1 overflow-y-auto max-h-[28rem] md:max-h-full space-y-4">
		{#if activeTab === 'personal'}
			<!-- Profile Image Section -->
			<div class="space-y-4">
				<UserProfileImage bind:profileImageUrl user={$user} />
			</div>

			<!-- Name Card -->
			<div class="space-y-2">
				<div class="mb-2">
					<div class="text-sm font-semibold">{$i18n.t('Name')}</div>
				</div>
				<input
					class="w-full px-4 py-2.5 text-sm bg-gray-50 dark:bg-gray-900 dark:text-gray-300 rounded-lg outline-none border border-gray-200 dark:border-gray-700 focus:border-gray-400 dark:focus:border-gray-600 transition"
					type="text"
					bind:value={name}
					required
					placeholder={$i18n.t('Enter your name')}
				/>
			</div>

			<!-- Bio Card -->
			<div class="space-y-2">
				<div class="mb-2">
					<div class="text-sm font-semibold">{$i18n.t('Bio')}</div>
				</div>
				<Textarea
					className="w-full px-4 py-2.5 text-sm bg-gray-50 dark:bg-gray-900 dark:text-gray-300 rounded-lg outline-none border border-gray-200 dark:border-gray-700 focus:border-gray-400 dark:focus:border-gray-600 transition"
					minSize={60}
					bind:value={bio}
					placeholder={$i18n.t('Share your background and interests')}
				/>
			</div>

			<!-- Gender Card -->
			<div class="space-y-2">
				<div class="mb-2">
					<div class="text-sm font-semibold">{$i18n.t('Gender')}</div>
				</div>
				<select
					class="w-full px-4 py-2.5 text-sm bg-gray-50 dark:bg-gray-900 dark:text-gray-300 rounded-lg outline-none border border-gray-200 dark:border-gray-700 focus:border-gray-400 dark:focus:border-gray-600 transition"
					bind:value={_gender}
					on:change={(e) => {
						console.log(_gender);
						if (_gender === 'custom') {
							gender = '';
						} else {
							gender = _gender;
						}
					}}
				>
					<option value="" selected>{$i18n.t('Prefer not to say')}</option>
					<option value="male">{$i18n.t('Male')}</option>
					<option value="female">{$i18n.t('Female')}</option>
					<option value="custom">{$i18n.t('Custom')}</option>
				</select>
				{#if _gender === 'custom'}
					<input
						class="w-full px-4 py-2.5 text-sm bg-gray-50 dark:bg-gray-900 dark:text-gray-300 rounded-lg outline-none border border-gray-200 dark:border-gray-700 focus:border-gray-400 dark:focus:border-gray-600 transition mt-2"
						type="text"
						required
						placeholder={$i18n.t('Enter your gender')}
						bind:value={gender}
					/>
				{/if}
			</div>

			<!-- Birth Date Card -->
			<div class="space-y-2">
				<div class="mb-2">
					<div class="text-sm font-semibold">{$i18n.t('Birth Date')}</div>
				</div>
				<input
					class="w-full px-4 py-2.5 text-sm bg-gray-50 dark:bg-gray-900 dark:text-gray-300 rounded-lg outline-none border border-gray-200 dark:border-gray-700 focus:border-gray-400 dark:focus:border-gray-600 transition"
					type="date"
					bind:value={dateOfBirth}
					required
				/>
			</div>

			<!-- Organization Info Card -->
			{#if userOrganization}
				<div class="space-y-2">
					<div class="mb-3">
						<div class="text-sm font-semibold">{$i18n.t('Organization')}</div>
					</div>
					<div class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-850 rounded-lg border border-gray-200 dark:border-gray-700">
						{#if userOrganization.dark_logo || userOrganization.light_logo}
							<img
								src={userOrganization.light_logo || userOrganization.dark_logo}
								alt="{userOrganization.org_name} logo"
								class="h-10 w-10 object-contain dark:hidden"
							/>
							<img
								src={userOrganization.dark_logo || userOrganization.light_logo}
								alt="{userOrganization.org_name} logo"
								class="h-10 w-10 object-contain hidden dark:block"
							/>
						{:else}
							<div class="h-10 w-10 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
								<span class="text-sm font-semibold text-gray-600 dark:text-gray-300">
									{userOrganization.org_name.substring(0, 2).toUpperCase()}
								</span>
							</div>
						{/if}
						<div class="flex-1">
							<div class="font-medium text-sm">{userOrganization.org_name}</div>
							<div class="text-xs text-gray-500 dark:text-gray-400">
								{$i18n.t('Organization Code')}: {userOrganization.org_code}
							</div>
						</div>
					</div>
				</div>
			{/if}

			<!-- Notification Webhook Card -->
			{#if $config?.features?.enable_user_webhooks}
				<div class="space-y-2">
					<div class="mb-2">
						<div class="text-sm font-semibold">{$i18n.t('Notification Webhook')}</div>
					</div>
					<input
						class="w-full px-4 py-2.5 text-sm bg-gray-50 dark:bg-gray-900 dark:text-gray-300 rounded-lg outline-none border border-gray-200 dark:border-gray-700 focus:border-gray-400 dark:focus:border-gray-600 transition"
						type="url"
						placeholder={$i18n.t('Enter your webhook URL')}
						bind:value={webhookUrl}
						required
					/>
				</div>
			{/if}
		{:else if activeTab === 'password'}
			<!-- Change Password Tab -->
			{#if $config?.features.enable_login_form}
				<div class="space-y-4">
					<div class="mb-4">
						<div class="text-sm font-semibold">{$i18n.t('Change Password')}</div>
					</div>
					<UpdatePassword />
				</div>
			{/if}
		{:else if activeTab === 'api'}
			<!-- API Keys Tab -->
			{#if ($config?.features?.enable_api_key ?? true) || $user?.role === 'admin'}
				<div class="bg-white dark:bg-gray-850 rounded-xl p-5 border border-gray-100 dark:border-gray-800">
					<div class="flex justify-between items-center mb-3">
						<div class="text-sm font-semibold">{$i18n.t('API keys')}</div>
						<button
							class="text-xs font-medium text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition"
							type="button"
							on:click={() => {
								showAPIKeys = !showAPIKeys;
							}}>{showAPIKeys ? $i18n.t('Hide') : $i18n.t('Show')}</button
						>
					</div>

					{#if showAPIKeys}
						<div class="space-y-4">
							{#if $user?.role === 'admin'}
								<div>
									<div class="text-xs font-medium mb-2 text-gray-600 dark:text-gray-400">
										{$i18n.t('JWT Token')}
									</div>
									<div class="flex gap-2">
										<div class="flex-1">
											<SensitiveInput value={localStorage.token} readOnly={true} />
										</div>
										<button
											class="px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 transition rounded-lg"
											on:click={() => {
												copyToClipboard(localStorage.token);
												JWTTokenCopied = true;
												setTimeout(() => {
													JWTTokenCopied = false;
												}, 2000);
											}}
										>
											{#if JWTTokenCopied}
												<svg
													xmlns="http://www.w3.org/2000/svg"
													viewBox="0 0 20 20"
													fill="currentColor"
													class="w-4 h-4"
												>
													<path
														fill-rule="evenodd"
														d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z"
														clip-rule="evenodd"
													/>
												</svg>
											{:else}
												<svg
													xmlns="http://www.w3.org/2000/svg"
													viewBox="0 0 16 16"
													fill="currentColor"
													class="w-4 h-4"
												>
													<path
														fill-rule="evenodd"
														d="M11.986 3H12a2 2 0 0 1 2 2v6a2 2 0 0 1-1.5 1.937V7A2.5 2.5 0 0 0 10 4.5H4.063A2 2 0 0 1 6 3h.014A2.25 2.25 0 0 1 8.25 1h1.5a2.25 2.25 0 0 1 2.236 2ZM10.5 4v-.75a.75.75 0 0 0-.75-.75h-1.5a.75.75 0 0 0-.75.75V4h3Z"
														clip-rule="evenodd"
													/>
													<path
														fill-rule="evenodd"
														d="M3 6a1 1 0 0 0-1 1v7a1 1 0 0 0 1 1h7a1 1 0 0 0 1-1V7a1 1 0 0 0-1-1H3Zm1.75 2.5a.75.75 0 0 0 0 1.5h3.5a.75.75 0 0 0 0-1.5h-3.5ZM4 11.75a.75.75 0 0 1 .75-.75h3.5a.75.75 0 0 1 0 1.5h-3.5a.75.75 0 0 1-.75-.75Z"
														clip-rule="evenodd"
													/>
												</svg>
											{/if}
										</button>
									</div>
								</div>
							{/if}

							{#if $config?.features?.enable_api_key ?? true}
								<div>
									{#if $user?.role === 'admin'}
										<div class="text-xs font-medium mb-2 text-gray-600 dark:text-gray-400">
											{$i18n.t('API Key')}
										</div>
									{/if}
									{#if APIKey}
										<div class="flex gap-2">
											<div class="flex-1">
												<SensitiveInput value={APIKey} readOnly={true} />
											</div>
											<button
												class="px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 transition rounded-lg"
												on:click={() => {
													copyToClipboard(APIKey);
													APIKeyCopied = true;
													setTimeout(() => {
														APIKeyCopied = false;
													}, 2000);
												}}
											>
												{#if APIKeyCopied}
													<svg
														xmlns="http://www.w3.org/2000/svg"
														viewBox="0 0 20 20"
														fill="currentColor"
														class="w-4 h-4"
													>
														<path
															fill-rule="evenodd"
															d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z"
															clip-rule="evenodd"
														/>
													</svg>
												{:else}
													<svg
														xmlns="http://www.w3.org/2000/svg"
														viewBox="0 0 16 16"
														fill="currentColor"
														class="w-4 h-4"
													>
														<path
															fill-rule="evenodd"
															d="M11.986 3H12a2 2 0 0 1 2 2v6a2 2 0 0 1-1.5 1.937V7A2.5 2.5 0 0 0 10 4.5H4.063A2 2 0 0 1 6 3h.014A2.25 2.25 0 0 1 8.25 1h1.5a2.25 2.25 0 0 1 2.236 2ZM10.5 4v-.75a.75.75 0 0 0-.75-.75h-1.5a.75.75 0 0 0-.75.75V4h3Z"
															clip-rule="evenodd"
														/>
														<path
															fill-rule="evenodd"
															d="M3 6a1 1 0 0 0-1 1v7a1 1 0 0 0 1 1h7a1 1 0 0 0 1-1V7a1 1 0 0 0-1-1H3Zm1.75 2.5a.75.75 0 0 0 0 1.5h3.5a.75.75 0 0 0 0-1.5h-3.5ZM4 11.75a.75.75 0 0 1 .75-.75h3.5a.75.75 0 0 1 0 1.5h-3.5a.75.75 0 0 1-.75-.75Z"
															clip-rule="evenodd"
														/>
													</svg>
												{/if}
											</button>
											<Tooltip content={$i18n.t('Create new key')}>
												<button
													class="px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 transition rounded-lg"
													aria-label={$i18n.t('Create new key')}
													on:click={() => {
														createAPIKeyHandler();
													}}
												>
													<svg
														xmlns="http://www.w3.org/2000/svg"
														fill="none"
														viewBox="0 0 24 24"
														stroke-width="2"
														stroke="currentColor"
														class="size-4"
													>
														<path
															stroke-linecap="round"
															stroke-linejoin="round"
															d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99"
														/>
													</svg>
												</button>
											</Tooltip>
										</div>
									{:else}
										<button
											class="flex gap-2 items-center font-medium px-4 py-2.5 rounded-lg bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 transition w-full justify-center"
											on:click={() => {
												createAPIKeyHandler();
											}}
										>
											<Plus strokeWidth="2" className="size-4" />
											{$i18n.t('Create new secret key')}
										</button>
									{/if}
								</div>
							{/if}
						</div>
					{/if}
				</div>
			{/if}
		{/if}
	</div>

	<div class="flex justify-end pt-3 text-sm font-medium border-t border-gray-200 dark:border-gray-700 mt-4">
		<button
			class="px-3.5 py-1.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full"
			on:click={async () => {
				const res = await submitHandler();

				if (res) {
					saveHandler();
				}
			}}
		>
			{$i18n.t('Save')}
		</button>
	</div>
</div>
