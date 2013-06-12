	var autocompleting = false;
	var addTagRegex = /item(\d+)AddTag/;

	function updateTagAutocomplete(){
		$.get(urlRoot + "tags/" + selectedList, function(data){
			var tagValues = jQuery.parseJSON(data);
			$('input[id$="AddTag"]').autocomplete({source: tagValues});
			$('input[id$="AddTag"]').on("autocompleteclose", function(event, ui){ 
				autocompleting = false;
			});
                        $('input[id$="AddTag"]').on("autocompleteopen", function(event, ui){
                                autocompleting = true;
                        });
                        $('input[id$="AddTag"]').on("autocompleteselect", function(event, ui){
                                autocompleting = false;
				item = findItemNumber(event.currentTarget.name);
				$("#item" + item + "AddTag").val(ui.item.value);
				addTag(findItemNumber(event.currentTarget.name));
                        });

		}).fail(function(data){ alert("An error occurred, unable to complete the request.")});

	}

	function findItemNumber(field){
		return addTagRegex.exec(field)[1];
	}

	function newTask(){
		$("#newTaskPos").toggle();
		$("#newTitle").focus();
	}

	function newList(){
		$("#newListPos").toggle();
		$("#newListName").focus();
	}
	
	function saveNew(){
		var title = "" + $("#newTitle").val();
		$.post(urlRoot + "newTask", {title: title, listId: selectedList }, function(data){
			$(".sortable").prepend(data);
			$("[id$=AddTagSpan]").hide();
			$("#newTitle").val("");
			$("#newTaskPos").hide();
			updateTagAutocomplete();
		}).fail(function(data){ alert("An error occurred, unable to complete the request.")});
	}
	function completeTask(taskId){
		$.post(urlRoot + "completeTask", {taskId: taskId}, function(data){
			setTimeout(function() { hideCompleted(taskId) }, 4000)
		}).fail(function(data){ alert("An error occurred, unable to complete the request.")});
	}
        function hideCompleted(taskId){
	    if($("#done" + taskId).is(':checked')){
		$("#item" + taskId).hide();
	    }
	}
	function changePriority(taskId, selectBox){
		$.post(urlRoot + "changePriority", {taskId: taskId, priorityIndex: selectBox.selectedIndex+1}, function(data){
			var key = "item" + taskId;
			var dataValue = Number(data);
			itemOrder[key] = dataValue;
			var prev = findPreviousId(dataValue);
			if(prev == null){
				var cur = $("#" + key).prev();
				while(cur.length > 0 && cur.prev().length > 0){
					cur = cur.prev();
				}
				$("#" + key).insertBefore(cur);
			} else {
				var prevElement = $("#" + prev);
				while(prevElement.next().length > 0 && itemOrder[prevElement.next().attr("id")] == itemOrder[prev]){
					prevElement = prevElement.next();
					prev = prevElement.attr("id");
				}
				$("#" + prev).after($("#" + key));
			}

		}).fail(function(data){ alert("An error occurred, unable to complete the request.")});		
	}
	function findPreviousId(value){
		var prev = null;
		for(var item in itemOrder){
			var nextValue = itemOrder[item];
			if(nextValue > value){
				if(prev == null || itemOrder[prev] > nextValue){
					prev = item;
				}
			}
			
		}
		return prev;
	}
	function changeList(){
		var listid = $("#selectList").val();
		window.location = urlRoot + "list/" + listid;
	}
	
	function changeTag(tagId){
		window.location = urlRoot + "listtag/" + tagId;
	}

	function changeTask(taskId, fields){
		$.ajax({url: urlRoot + "api/task/" + taskId,
			type: "PUT",
			data: JSON.stringify(fields),
			headers: {"Content-Type": "application/json"},
			dataType: "json"});
		// TODO: Handle error
	}

	function deleteItem(taskId){
		if(confirm("Are You Sure You Would Like To Delete This Task?")){
			$.ajax({url: urlRoot + "api/task/" + taskId,
			type: "DELETE",
			success: function(){
				$("#item" + taskId).hide();
			}});
		} 
		// TODO: Handle error
	}
	
	function removeTag(taskId, tagId, tagName){
		if(!confirm("Remove Tag " + tagName + "?")){
			return false;
		}
		$.post(urlRoot + "removeTag", {"taskId": taskId, "tag": tagId}, function(data) {
			updateTaskView(taskId);
		}).fail(function(data){ alert("An error occurred, unable to complete the request.")});
	}

	function addTag(taskId){
		if(autocompleting){
			return false;
		}
		var tags = $("#item" + taskId + "AddTag").val();
		if(tags.trim() == ""){
			return;
		}
		$.post(urlRoot + "addTag", {"taskId" : taskId, "tag": tags}, function(data) {
			$("#item" + taskId + "AddTagSpan").hide();
			$("#item" + taskId + "AddTag").val("");
			updateTagAutocomplete();
			updateTaskView(taskId);
			$("#tagdiv").html(data);
		}).fail(function() { alert("Error adding tag") });
	}

	function tagBox(tagId){
		$("#item" + tagId + "AddTagSpan").toggle();
		$("#item" + tagId + "AddTag").focus();
	}
	var editingTitle = -1;
	function editTitle(taskId){
		if(editingTitle != -1){
			updateTitle(editingTitle, $("#titleBox"+taskId));
			return;
		}
		loadTask(taskId, function(task){
			editingTitle = taskId;
			var html = "<input type='text' value='" + task.title + 
				"' onchange='updateTitle(" + taskId + ", this)' id='titleBox" + taskId +
				"' class='titleBox'></input>";
			$("#item" + taskId + "Title").html(html);			
		});
	}
	function updateTitle(taskId, inputField){
		editingTitle = -1;
		var title = $(inputField).val();
		$("#item" + taskId + "Title").html(title);
		changeTask(taskId, {"title": title});
	}
	function loadTask(taskId, callback){
        $.get(urlRoot + "api/task/" + taskId, callback)
                .fail(function(data){ alert("An error occurred, unable to complete the request.")});
	}
	function updateTaskView(taskId){
		loadTask(taskId, function(task) {
			var tagText = "";
			tags = jQuery.map(task.tags, function(tag) {
				tagText += '<span title="Delete Tag" onclick="removeTag(' + taskId + ',' + tag.id;
				tagText += ',\'' + tag.name + '\')">'; 
				tagText += tag.name + "</span> &nbsp;";
				return tag.name;
			});
			$("#item" + task.id + "Tags").html(tagText);
		});
	}
	function noteBox(taskId){
		var pos = $("#item" + taskId);
		var name = 'notesBox'+taskId;
		if($("#" + name + "li").length > 0){
			cancelNote(taskId);
			return;
		}
		loadTask(taskId, function(task) {
			var textbox = "<li id='"+name+"li'><textarea class='notesBox' id='"+name+"' name='"+name+"'></textarea>" +
				"<button onclick='saveNote("+taskId+")'>Save</button> <button onclick='cancelNote("+taskId+")'>Cancel</button>";
			pos.append(textbox);
			$("#" + name).val(task.details);
		});
	}
	function cancelNote(taskId){
		$("#notesBox" + taskId + "li").remove();
	}
	function saveNote(taskId){
		var details = $("#notesBox"+taskId).val();
		changeTask(taskId, {"details": details});
		cancelNote(taskId);	
	}
	function deleteList(){
		if(!confirm("Are you sure you would like to delete the current list?")){
			return false;
		}
		$.post(urlRoot + "removeList", {listId: selectedList }, function(data){
			window.location=urlRoot + "list";
		}).fail(function(data){ alert("An error occurred, unable to complete the request.")});
	}