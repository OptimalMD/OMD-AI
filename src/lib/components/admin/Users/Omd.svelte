<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';

	import { user } from '$lib/stores';
	import { getGroups } from '$lib/apis/groups';
	import { getModelItems, updateModelById, getBaseModels } from '$lib/apis/models';

	// Types
	type Group = { id: string; name: string; [key: string]: any };
	type Model = { id: string; name: string; access_control?: any; info?: any; [key: string]: any };

	import Search from '$lib/components/icons/Search.svelte';
	import Cube from '$lib/components/icons/Cube.svelte';
	import Plus from '$lib/components/icons/Plus.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';
	import SpinnerFull from '$lib/components/common/SpinnerFull.svelte';

	import Modal from '$lib/components/common/Modal.svelte';

	const i18n = getContext('i18n');

	let loaded: boolean = false;
	let omdGroup: Group | null = null;

	let allModels: Model[] = [];
	let allModelsList: Model[] = [];
	let workspaceModels: Model[] = [];
	let omdModels: Model[] = [];
	let filteredModels: Model[] = [];
	let search: string = '';

	let showAddModelModal: boolean = false;
	let selectedModelId: string = '';
	let saveLoading: boolean = false;

	$: filteredModels = omdModels.filter((model: Model) => {
		if (search === '') {
			return true;
		} else {
			const name = model.name.toLowerCase();
			const id = model.id.toLowerCase();
			const query = search.toLowerCase();
			return name.includes(query) || id.includes(query);
		}
	});

	const fetchData = async () => {
		// Get all groups
		const groups: Group[] = await getGroups(localStorage.token);
		omdGroup = groups.find((g: Group) => g.name.toLowerCase() === 'omd') || null;

		if (!omdGroup) {
			toast.error(i18n.t('OMD group not found'));
			return;
		}

		// Get all models from getBaseModels API utility

		try {
			const res = await getBaseModels(localStorage.token);
			allModelsList = res?.data || res || [];
		} catch (e) {
			allModelsList = [];
		}

		try {
			workspaceModels = await getModelItems(localStorage.token);
		} catch (e) {
			workspaceModels = [];
		}
		// Merge: prioritize workspace model data if it exists
		const modelMap = new Map<string, Model>();
		allModelsList.forEach((model: Model) => {
			modelMap.set(model.id, model);
		});
		workspaceModels.forEach((model: Model) => {
			modelMap.set(model.id, model);
		});
		allModels = Array.from(modelMap.values());

		// Filter models that have OMD group in their access control
		omdModels = allModels.filter((model: Model) => {
			// Check if model has access_control
			const accessControl = model.access_control || model.info?.access_control;
			if (!accessControl) return false;

			// Check both read and write access for the group
			const readGroupIds = accessControl.read?.group_ids || [];
			const writeGroupIds = accessControl.write?.group_ids || [];
			return readGroupIds.includes(omdGroup!.id) || writeGroupIds.includes(omdGroup!.id);
		});

		loaded = true;
	};

	// Get all models that are not in OMD group
	$: availableModels = allModels.filter((model: Model) => {
		const accessControl = model.access_control || model.info?.access_control;
		if (!accessControl) return true;
		const readGroupIds = accessControl.read?.group_ids || [];
		const writeGroupIds = accessControl.write?.group_ids || [];
		return (
			!readGroupIds.includes(omdGroup?.id ?? '') && !writeGroupIds.includes(omdGroup?.id ?? '')
		);
	});

	async function handleSaveModelToGroup() {
		if (!selectedModelId || !omdGroup) return;
		saveLoading = true;
		try {
			// Find the model
			const model = allModels.find((m: Model) => m.id === selectedModelId);
			if (!model) throw new Error('Model not found');
			// Prepare access_control update
			let ac = model.access_control ||
				model.info?.access_control || { read: { group_ids: [] }, write: { group_ids: [] } };
			// Ensure group_ids are arrays
			ac.read = ac.read || { group_ids: [] };
			ac.write = ac.write || { group_ids: [] };
			if (!Array.isArray(ac.read.group_ids)) ac.read.group_ids = [];
			if (!Array.isArray(ac.write.group_ids)) ac.write.group_ids = [];
			// Add group id to read if not present (do NOT add to write)
			if (!ac.read.group_ids.includes(omdGroup.id)) ac.read.group_ids.push(omdGroup.id);
			// Remove from write if present
			ac.write.group_ids = ac.write.group_ids.filter((id: string) => id !== omdGroup.id);
			// Build full model payload as required by backend ModelForm
			const updatePayload: any = {
				...model,
				access_control: ac
			};
			// Save
			const result = await updateModelById(localStorage.token, model.id, updatePayload);
			if (!result || result.error) {
				console.error('Update failed', result);
				throw new Error(result?.error || 'Update failed');
			}
			toast.success($i18n.t('Model added to OMD group'));
			showAddModelModal = false;
			selectedModelId = '';
			await fetchData();
		} catch (e) {
			console.error('Failed to add model to group:', e);
			toast.error($i18n.t('Failed to add model'));
		} finally {
			saveLoading = false;
		}
	}

	// Remove OMDs group from model
	async function handleRemoveModelFromGroup(modelId: string) {
		if (!omdGroup) return;
		try {
			const model = allModels.find((m: Model) => m.id === modelId);
			if (!model) throw new Error('Model not found');
			let ac = model.access_control ||
				model.info?.access_control || { read: { group_ids: [] }, write: { group_ids: [] } };
			ac.read = ac.read || { group_ids: [] };
			ac.write = ac.write || { group_ids: [] };
			if (!Array.isArray(ac.read.group_ids)) ac.read.group_ids = [];
			if (!Array.isArray(ac.write.group_ids)) ac.write.group_ids = [];
			// Remove OMD group from both read and write
			ac.read.group_ids = ac.read.group_ids.filter((id: string) => id !== omdGroup.id);
			ac.write.group_ids = ac.write.group_ids.filter((id: string) => id !== omdGroup.id);
			const updatePayload: any = {
				...model,
				access_control: ac
			};
			const result = await updateModelById(localStorage.token, model.id, updatePayload);
			if (!result || result.error) {
				throw new Error(result?.error || 'Update failed');
			}
			toast.success($i18n.t('Model removed from OMD group'));
			await fetchData();
		} catch (e) {
			console.error('Failed to remove model from group:', e);
			toast.error($i18n.t('Failed to remove model'));
		}
	}

	onMount(async () => {
		if ($user?.role !== 'admin') {
			await goto('/');
			return;
		}

		await fetchData();
	});
</script>

{#if loaded}
	<div class="mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
		<div class="flex items-center gap-3">
			<div
				class="w-12 h-12 rounded-full bg-green-600 dark:bg-green-500 flex items-center justify-center text-white font-bold text-lg"
			>
				OMD
			</div>
			<div>
				<h2 class="text-2xl font-semibold text-gray-900 dark:text-white">
					OMD {$i18n.t('Models')}
				</h2>
				<p class="text-sm text-gray-500 dark:text-gray-400">
					{omdModels.length}
					{$i18n.t('models available')}
				</p>
			</div>
		</div>

		<div class="flex gap-3 w-full md:w-auto items-center">
			<div class="relative flex-1 md:w-64">
				<div class="absolute inset-y-0 left-3 flex items-center pointer-events-none">
					<Search className="size-4 text-gray-400" />
				</div>
				<input
					class="w-full pl-10 pr-4 py-2 text-sm rounded-lg bg-white dark:bg-gray-850 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600 focus:border-transparent outline-none transition"
					bind:value={search}
					placeholder={$i18n.t('Search models...')}
				/>
			</div>
			<button
				class="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition text-sm font-medium"
				on:click={() => (showAddModelModal = true)}
			>
				<Plus className="w-4 h-4" />
				{$i18n.t('Add Model')}
			</button>
		</div>
	</div>

	<div>
		{#if filteredModels.length === 0}
			<div class="flex flex-col items-center justify-center py-16">
				<div class="text-gray-400 dark:text-gray-600 mb-4">
					<Cube className="size-16" />
				</div>
				<div class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
					{search ? $i18n.t('No models found') : $i18n.t('No models assigned')}
				</div>
				<div class="text-sm text-gray-500 dark:text-gray-400">
					{search
						? $i18n.t('Try adjusting your search query')
						: $i18n.t('Assign models to the OMD group to see them here')}
				</div>
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each filteredModels as model}
					<div
						class="bg-white dark:bg-gray-850 border border-gray-200 dark:border-gray-700 rounded-lg p-5 hover:border-blue-300 dark:hover:border-blue-600 transition"
					>
						<div class="flex items-start justify-between mb-3">
							<div class="flex-1 min-w-0">
								<h3 class="text-base font-medium text-gray-900 dark:text-white truncate mb-1">
									{model.name}
								</h3>
								<p class="text-xs text-gray-500 dark:text-gray-400 truncate font-mono">
									{model.id}
								</p>
							</div>
							<div class="flex flex-col items-end gap-2">
								<button
									class="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-xs font-medium rounded hover:bg-red-200 dark:hover:bg-red-800 transition"
									on:click={() => handleRemoveModelFromGroup(model.id)}
								>
									{$i18n.t('Remove')}
								</button>
							</div>
						</div>

						{#if model.info?.meta?.description}
							<p class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
								{model.info.meta.description}
							</p>
						{/if}
					</div>
				{/each}
			</div>
		{/if}
	</div>
{:else}
	<SpinnerFull />
{/if}

{#if showAddModelModal}
	<Modal bind:show={showAddModelModal} size="sm">
		<div class="p-4">
			<div class="flex justify-between items-center mb-4">
				<h3 class="text-lg font-semibold">{$i18n.t('Add Model to OMD Group')}</h3>
				<button
					class="text-gray-400 hover:text-gray-600"
					on:click={() => (showAddModelModal = false)}><XMark className="w-5 h-5" /></button
				>
			</div>
			<div class="mb-4">
				<label class="block mb-2 text-sm font-medium" for="add-model-select"
					>{$i18n.t('Select Model')}</label
				>
				<select
					id="add-model-select"
					class="w-full p-2 border rounded"
					bind:value={selectedModelId}
				>
					<option value="" disabled selected>{$i18n.t('Choose a model')}</option>
					{#if allModels.length > 0}
						{#if $user?.role === 'admin'}
							<optgroup label="Workspace Models">
								{#each allModels.filter(m => workspaceModels.find(wm => wm.id === m.id)) as model}
									{#if omdModels.find((m2: Model) => m2.id === model.id)}
										<option value={model.id} disabled>{model.name} ({$i18n.t('Added')})</option>
									{:else}
										<option value={model.id}>{model.name}</option>
									{/if}
								{/each}
							</optgroup>
							<optgroup label="Base Models">
								{#each allModels.filter(m => !workspaceModels.find(wm => wm.id === m.id)) as model}
									{#if omdModels.find((m2: Model) => m2.id === model.id)}
										<option value={model.id} disabled>{model.name} ({$i18n.t('Added')})</option>
									{:else}
										<option value={model.id}>{model.name}</option>
									{/if}
								{/each}
							</optgroup>
						{/if}
					{/if}
				</select>
			</div>
			<div class="flex justify-end gap-2">
				<button
					class="px-4 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300"
					on:click={() => (showAddModelModal = false)}>{$i18n.t('Cancel')}</button
				>
				<button
					class="px-4 py-2 rounded bg-green-600 text-white hover:bg-green-700 disabled:opacity-50"
					on:click={handleSaveModelToGroup}
					disabled={!selectedModelId || saveLoading}
				>
					{saveLoading ? $i18n.t('Saving...') : $i18n.t('Save')}
				</button>
			</div>
		</div>
	</Modal>
{/if}
