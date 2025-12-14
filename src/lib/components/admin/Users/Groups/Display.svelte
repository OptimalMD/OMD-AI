<script lang="ts">
	import { getContext } from 'svelte';
	import Textarea from '$lib/components/common/Textarea.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';

	const i18n = getContext('i18n');

	export let name = '';
	export let color = '';
	export let description = '';
</script>

<div class="flex flex-col w-full">
	<label class="block text-sm font-normal text-gray-700 dark:text-gray-300 mb-1.5" for="group-name">
		{$i18n.t('Name')}
	</label>
	<input
		id="group-name"
		type="text"
		class="w-full px-3.5 py-2 text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent placeholder-gray-400 dark:placeholder-gray-500"
		placeholder={$i18n.t('Group Name')}
		bind:value={name}
		autocomplete="off"
		required
	/>
</div>

<!-- <div class="flex flex-col w-full mt-2">
	<div class=" mb-1 text-xs text-gray-500">{$i18n.t('Color')}</div>

	<div class="flex-1">
		<Tooltip content={$i18n.t('Hex Color - Leave empty for default color')} placement="top-start">
			<div class="flex gap-0.5">
				<div class="text-gray-500">#</div>

				<input
					class="w-full text-sm bg-transparent placeholder:text-gray-300 dark:placeholder:text-gray-700 outline-hidden"
					type="text"
					bind:value={color}
					placeholder={$i18n.t('Hex Color')}
					autocomplete="off"
				/>
			</div>
		</Tooltip>
	</div>
</div> -->

<div class="flex flex-col w-full mt-4">
	<label class="block text-sm font-normal text-gray-700 dark:text-gray-300 mb-1.5" for="group-description">
		{$i18n.t('Description')}
	</label>
	<textarea
		id="group-description"
		rows="4"
		class="w-full px-3.5 py-2 text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent resize-none placeholder-gray-400 dark:placeholder-gray-500"
		placeholder={$i18n.t('Group Description')}
		bind:value={description}
	></textarea>
</div>
