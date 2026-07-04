/* BRIDGE SCRIPT */

// Constants
var name = "$NAME$";
var thresold = $THRESOLD$;
var env = {};

// Setup bridge
var data_out = ["", array_create(16, undefined)];
var data_in = [-1, undefined];

var data_bridge = method({ thresold, env }, function(name) {
    for (var a = 0;a < 15;a++) {
        env.out[1][a] = argument[a + 1];
    }
    env.out[0] = name;
    env.in[1] = undefined;
    env.in[0] = -1;

    var t = current_time;

    while env.in[0] == -1 {
        if (current_time - t) / 1000 > thresold {
            break;
        }
    }

    env.out[0] = "";

    if env.in[0] == true {
        return env.in[1];
    }

    return undefined;
})

var data_register = method({ env }, function(func) {
    return method({ bridge: env.bridge }, func)
})

env.out = data_out;
env.in = data_in;
env.bridge = data_bridge;

variable_struct_set(global, name, env);

/* ENV FUNCTIONS */

// gml
gml_wait = data_register(function(delay) {
    var t = current_time;

    while true {
        if (current_time - t) / 1000 > delay {
            break
        }
    }

    return true
});

gml_load = data_register(function(gml, vmself, vmother) {
    return bridge("gml_load", gml, vmself, vmother)
})

gml_load_async = data_register(function(gml, vmself, vmother) {
    return bridge("gml_load_async", gml, vmself, vmother)
})

// debug
debug_get_locals = data_register(function(level=0) {
    return bridge("debug_get_locals", level)
});

debug_get_self = data_register(function(level=0) {
    return bridge("debug_get_self", level)
});

debug_get_other = data_register(function(level=0) {
    return bridge("debug_get_other", level)
});

debug_get_script = data_register(function(level=0) {
    return bridge("debug_get_script", level)
});

// arrays
array_freeze = data_register(function(array) {
    bridge("array_freeze", array)

    return array
});

array_unfreeze = data_register(function(array) {
    bridge("array_unfreeze", array)

    return array
});

array_frozen = data_register(function(array) {
    return bridge("array_frozen", array)
});

// methods
script_replace = data_register(function(target, value) {
    if is_method(target) { target = method_get_index(target) }
    if is_method(value) { value = method_get_index(value) }

    bridge("script_replace", target, value)

    return value
});

// http
http_get_direct = data_register(function(url) {
    if not string_starts_with(url, "https://") {
        url = "https://" + url
    }

    return bridge("http_get_direct", url)
})

// Send init status
data_bridge("init", true);