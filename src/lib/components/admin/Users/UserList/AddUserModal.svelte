<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { createEventDispatcher } from 'svelte';
	import { onMount, getContext } from 'svelte';
	import { addUser } from '$lib/apis/auths';

	import { WEBUI_BASE_URL } from '$lib/constants';

	import Spinner from '$lib/components/common/Spinner.svelte';
	import Modal from '$lib/components/common/Modal.svelte';
	import { generateInitialsImage } from '$lib/utils';
	import XMark from '$lib/components/icons/XMark.svelte';
	import SensitiveInput from '$lib/components/common/SensitiveInput.svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let show = false;

	let loading = false;
	let tab = '';
	let inputFiles;

	let _user = {
		name: '',
		email: '',
		password: '',
		role: 'user'
	};

	$: if (show) {
		_user = {
			name: '',
			email: '',
			password: '',
			role: 'user'
		};
	}

	const submitHandler = async () => {
		const stopLoading = () => {
			dispatch('save');
			loading = false;
		};

		if (tab === '') {
			loading = true;

			const res = await addUser(
				localStorage.token,
				_user.name,
				_user.email,
				_user.password,
				_user.role,
				generateInitialsImage(_user.name)
			).catch((error) => {
				toast.error(`${error}`);
			});

			if (res) {
				stopLoading();
				show = false;
			}
		} else {
			if (inputFiles) {
				loading = true;

				const file = inputFiles[0];
				const reader = new FileReader();

				reader.onload = async (e) => {
					const csv = e.target.result;
					const rows = csv.split('\n');

					let userCount = 0;

					for (const [idx, row] of rows.entries()) {
						const columns = row.split(',').map((col) => col.trim());
						console.debug(idx, columns);

						if (idx > 0) {
							if (
								columns.length === 4 &&
								['admin', 'user', 'pending'].includes(columns[3].toLowerCase())
							) {
								const res = await addUser(
									localStorage.token,
									columns[0],
									columns[1],
									columns[2],
									columns[3].toLowerCase(),
									generateInitialsImage(columns[0])
								).catch((error) => {
									toast.error(`Row ${idx + 1}: ${error}`);
									return null;
								});

								if (res) {
									userCount = userCount + 1;
								}
							} else {
								toast.error(`Row ${idx + 1}: invalid format.`);
							}
						}
					}

					toast.success(
						$i18n.t('Successfully imported {{userCount}} users.', { userCount: userCount })
					);
					inputFiles = null;
					const uploadInputElement = document.getElementById('upload-user-csv-input');

					if (uploadInputElement) {
						uploadInputElement.value = null;
					}

					stopLoading();
				};

				reader.readAsText(file, 'utf-8');
			} else {
				toast.error($i18n.t('File not found.'));
			}
		}

		loading = false;
	};
</script>

<Modal size="sm" bind:show>
	<div>
		<div class="flex justify-between dark:text-gray-300 px-5 py-4 border-b border-gray-200 dark:border-gray-800">
			<div class="text-lg font-semibold self-center text-gray-900 dark:text-white">{$i18n.t('Add User')}</div>
			<button
				class="self-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition"
				on:click={() => {
					show = false;
				}}
			>
				<XMark className={'size-5'} />
			</button>
		</div>

		<div class="flex flex-col md:flex-row w-full px-4 pb-3 md:space-x-4 dark:text-gray-200">
			<div class=" flex flex-col w-full sm:flex-row sm:justify-center sm:space-x-6">
				<form
					class="flex flex-col w-full"
					on:submit|preventDefault={() => {
						submitHandler();
					}}
				>
					<div class="flex gap-4 mb-4 border-b border-gray-200 dark:border-gray-800">
						<button
							class="pb-2 text-sm font-medium transition {tab === ''
								? 'text-gray-900 dark:text-white border-b-2 border-gray-900 dark:border-white'
								: 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'}"
							type="button"
							on:click={() => {
								tab = '';
							}}>{$i18n.t('Form')}</button
						>

						<button
							class="pb-2 text-sm font-medium transition {tab === 'import'
								? 'text-gray-900 dark:text-white border-b-2 border-gray-900 dark:border-white'
								: 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'}"
							type="button"
							on:click={() => {
								tab = 'import';
							}}>{$i18n.t('CSV Import')}</button
						>
					</div>

					<div class="px-1">
						{#if tab === ''}
							<div class="flex flex-col w-full mb-4">
								<label class="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">{$i18n.t('Role')}</label>

								<div class="flex-1">
									<select
										class="w-full capitalize rounded-lg px-3 py-2.5 text-sm bg-white dark:bg-gray-850 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600 focus:border-transparent outline-none transition"
										bind:value={_user.role}
										placeholder={$i18n.t('Enter Your Role')}
										required
									>
										<option value="pending"> {$i18n.t('pending')} </option>
										<option value="user"> {$i18n.t('user')} </option>
										<option value="admin"> {$i18n.t('admin')} </option>
									</select>
								</div>
							</div>

							<div class="flex flex-col w-full mb-4">
								<label class="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">{$i18n.t('Name')}</label>

								<div class="flex-1">
									<input
										class="w-full rounded-lg px-3 py-2.5 text-sm bg-white dark:bg-gray-850 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600 focus:border-transparent outline-none transition"
										type="text"
										bind:value={_user.name}
										placeholder={$i18n.t('Enter Your Full Name')}
										autocomplete="off"
										required
									/>
								</div>
							</div>

							<div class="flex flex-col w-full mb-4">
								<label class="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">{$i18n.t('Email')}</label>

								<div class="flex-1">
									<input
										class="w-full rounded-lg px-3 py-2.5 text-sm bg-white dark:bg-gray-850 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600 focus:border-transparent outline-none transition"
										type="email"
										bind:value={_user.email}
										placeholder={$i18n.t('Enter Your Email')}
										required
									/>
								</div>
							</div>

						<div class="flex flex-col w-full">
							<label class="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">{$i18n.t('Password')}</label>

							<div class="flex-1">
								<SensitiveInput
									outerClassName="flex flex-1 bg-white dark:bg-gray-850 border border-gray-300 dark:border-gray-700 rounded-lg focus-within:ring-2 focus-within:ring-blue-500 dark:focus-within:ring-blue-600 focus-within:border-transparent transition"
									inputClassName="w-full rounded-lg px-3 py-2.5 text-sm bg-transparent text-gray-900 dark:text-white placeholder-gray-400 outline-none"
									showButtonClassName="pr-3 transition text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
									type="password"
									bind:value={_user.password}
									placeholder={$i18n.t('Enter Your Password')}
									autocomplete="off"
									required
								/>
							</div>
						</div>
						{:else if tab === 'import'}
							<div>
								<div class="mb-4 w-full">
									<input
										id="upload-user-csv-input"
										hidden
										bind:files={inputFiles}
										type="file"
										accept=".csv"
									/>

									<button
										class="w-full text-sm font-medium py-8 bg-white dark:bg-gray-850 hover:bg-gray-50 dark:hover:bg-gray-800 border-2 border-dashed border-gray-300 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-600 text-gray-600 dark:text-gray-400 text-center rounded-lg transition"
										type="button"
										on:click={() => {
											document.getElementById('upload-user-csv-input')?.click();
										}}
									>
										{#if inputFiles}
											{inputFiles.length > 0 ? `${inputFiles.length}` : ''} document(s) selected.
										{:else}
											{$i18n.t('Click here to select a csv file.')}
										{/if}
									</button>
								</div>

								<div class="text-xs text-gray-600 dark:text-gray-400 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
									<div class="mb-2">
										ⓘ {$i18n.t(
											'Ensure your CSV file includes 4 columns in this order: Name, Email, Password, Role.'
										)}
									</div>
									<a
										class="underline text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition"
										href="{WEBUI_BASE_URL}/static/user-import.csv"
									>
										{$i18n.t('Click here to download user import template file.')}
									</a>
								</div>
							</div>
						{/if}
					</div>

					<div class="flex justify-end pt-4 border-t border-gray-200 dark:border-gray-800 mt-6">
						<button
							class="px-6 py-2.5 text-sm font-medium bg-green-600 hover:bg-green-700 text-white transition rounded-lg flex flex-row space-x-2 items-center disabled:opacity-50 disabled:cursor-not-allowed"
							type="submit"
							disabled={loading}
						>
							<span>{$i18n.t('Save')}</span>

							{#if loading}
								<div class="self-center">
									<Spinner className="size-4" />
								</div>
							{/if}
						</button>
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
