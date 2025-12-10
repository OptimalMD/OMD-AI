<script>
	import { toast } from 'svelte-sonner';
	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';

	import { user } from '$lib/stores';
	import { getGroups } from '$lib/apis/groups';
	import { getModelItems, updateModelById, createNewModel } from '$lib/apis/models';
	import { getModels } from '$lib/apis';

	import Search from '$lib/components/icons/Search.svelte';
	import Cube from '$lib/components/icons/Cube.svelte';
	import Plus from '$lib/components/icons/Plus.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';

	const i18n = getContext('i18n');

	let loaded = false;
	let omdGroup = null;
	let allModels = [];
	let omdModels = [];
	let filteredModels = [];
	let search = '';
	let showAddModal = false;
	let availableModels = [];
	let selectedModelId = '';
	let saving = false;

	$: filteredModels = omdModels.filter((model) => {
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
		const groups = await getGroups(localStorage.token);
		omdGroup = groups.find(g => g.name.toLowerCase() === 'omd');

		if (!omdGroup) {
			toast.error($i18n.t('OMD group not found'));
			return;
		}

		// Get all models (base + workspace)
		const res = await getModels(localStorage.token);
		const allModelsList = res?.data || res || [];
		
		// Get workspace models to check which have access control
		const workspaceModels = await getModelItems(localStorage.token);
		
		// Merge: prioritize workspace model data if it exists
		const modelMap = new Map();
		allModelsList.forEach(model => {
			modelMap.set(model.id, model);
		});
		workspaceModels.forEach(model => {
			modelMap.set(model.id, model);
		});
		allModels = Array.from(modelMap.values());

		// Filter models that have OMD group in their access control
		omdModels = allModels.filter(model => {
			// Check if model has access_control
			const accessControl = model.access_control || model.info?.meta?.access_control;
			if (!accessControl) return false;

			// Check both read and write access for the group
			const readGroupIds = accessControl.read?.group_ids || [];
			const writeGroupIds = accessControl.write?.group_ids || [];
			
			return readGroupIds.includes(omdGroup.id) || writeGroupIds.includes(omdGroup.id);
		});

		loaded = true;
	};

	const openAddModal = () => {
		// Get models that don't have OMD group assigned
		availableModels = allModels.filter(model => {
			const accessControl = model.access_control || model.info?.meta?.access_control;
			if (!accessControl) return true;

			const readGroupIds = accessControl.read?.group_ids || [];
			const writeGroupIds = accessControl.write?.group_ids || [];
			
			return !readGroupIds.includes(omdGroup.id) && !writeGroupIds.includes(omdGroup.id);
		});

		selectedModelId = '';
		showAddModal = true;
	};

	const addModelToGroup = async () => {
		if (!selectedModelId) {
			toast.error($i18n.t('Please select a model'));
			return;
		}

		saving = true;

		try {
			const model = allModels.find(m => m.id === selectedModelId);
			if (!model) {
				toast.error($i18n.t('Model not found'));
				return;
			}
			
			// Check if this is a workspace model or base model
			const workspaceModels = await getModelItems(localStorage.token);
			const existingWorkspaceModel = workspaceModels.find(m => m.id === selectedModelId);

			if (existingWorkspaceModel) {
				// Update existing workspace model
				const accessControl = existingWorkspaceModel.access_control || {
					read: { group_ids: [], user_ids: [] },
					write: { group_ids: [], user_ids: [] }
				};

				if (!accessControl.read.group_ids.includes(omdGroup.id)) {
					accessControl.read.group_ids.push(omdGroup.id);
				}

				const updatedModel = {
					id: existingWorkspaceModel.id,
					name: existingWorkspaceModel.name || existingWorkspaceModel.id,
					meta: existingWorkspaceModel.meta || {},
					params: existingWorkspaceModel.params || {},
					access_control: accessControl,
					is_active: existingWorkspaceModel.is_active ?? true
				};

				await updateModelById(localStorage.token, selectedModelId, updatedModel);
			} else {
				// Create new workspace model entry for base model
				const newModel = {
					id: model.id,
					name: model.name || model.id,
					meta: model.info?.meta || model.meta || {
						description: model.details?.description || '',
						capabilities: model.details?.capabilities || {}
					},
					params: model.details?.params || model.params || {},
					access_control: {
						read: { group_ids: [omdGroup.id], user_ids: [] },
						write: { group_ids: [], user_ids: [] }
					},
					is_active: true
				};

				await createNewModel(localStorage.token, newModel);
			}
			
			toast.success($i18n.t('Model added to OMD group successfully'));
			showAddModal = false;
			selectedModelId = '';
			await fetchData();
		} catch (error) {
			toast.error($i18n.t('Failed to add model to group'));
			console.error(error);
		} finally {
			saving = false;
		}
	};

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
			<div class="w-12 h-12 rounded-full bg-blue-600 dark:bg-blue-500 flex items-center justify-center text-white font-bold text-lg">
				OMD
			</div>
			<div>
				<h2 class="text-2xl font-semibold text-gray-900 dark:text-white">OMD {$i18n.t('Models')}</h2>
				<p class="text-sm text-gray-500 dark:text-gray-400">
					{omdModels.length} {$i18n.t('models available')}
				</p>
			</div>
		</div>

		<div class="flex gap-3 w-full md:w-auto">
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
				class="px-4 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white transition rounded-lg flex items-center gap-2 whitespace-nowrap"
				on:click={openAddModal}
			>
				<Plus className="size-4" />
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
					<div class="bg-white dark:bg-gray-850 border border-gray-200 dark:border-gray-700 rounded-lg p-5 hover:border-blue-300 dark:hover:border-blue-600 transition">
						<div class="flex items-start justify-between mb-3">
							<div class="flex-1 min-w-0">
								<h3 class="text-base font-medium text-gray-900 dark:text-white truncate mb-1">
									{model.name}
								</h3>
								<p class="text-xs text-gray-500 dark:text-gray-400 truncate font-mono">
									{model.id}
								</p>
							</div>
							<div class="ml-2 px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs font-medium rounded">
								OMD
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

	<!-- Add Model Modal -->
	{#if showAddModal}
		<div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" on:click={() => showAddModal = false}>
			<div class="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-md w-full mx-4" on:click={(e) => e.stopPropagation()}>
				<div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
					<h3 class="text-xl font-semibold text-gray-900 dark:text-white">
						{$i18n.t('Add Model to OMD')}
					</h3>
					<button
						class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
						on:click={() => showAddModal = false}
					>
						<XMark className="size-5" />
					</button>
				</div>

				<div class="p-6">
					{#if availableModels.length === 0}
						<p class="text-gray-500 dark:text-gray-400 text-center py-4">
							{$i18n.t('All models are already assigned to OMD group')}
						</p>
					{:else}
						<div class="mb-4">
							<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
								{$i18n.t('Select Model')}
							</label>
							<select
								bind:value={selectedModelId}
								class="w-full px-3 py-2 text-sm rounded-lg bg-white dark:bg-gray-850 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600 focus:border-transparent outline-none transition"
							>
								<option value="">{$i18n.t('Choose a model...')}</option>
								{#each availableModels as model}
									<option value={model.id}>{model.name}</option>
								{/each}
							</select>
						</div>

						<div class="flex justify-end gap-3 mt-6">
							<button
								class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition"
								on:click={() => showAddModal = false}
								disabled={saving}
							>
								{$i18n.t('Cancel')}
							</button>
							<button
								class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
								on:click={addModelToGroup}
								disabled={saving || !selectedModelId}
							>
								{#if saving}
									<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
								{/if}
								{$i18n.t('Add to Group')}
							</button>
						</div>
					{/if}
				</div>
			</div>
		</div>
	{/if}
{:else}
	<div class="flex justify-center items-center h-64">
		<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
	</div>
{/if}
