local function system_ruby()
    local parameter_info = {
        rt = { type = 8, list_items = {} }
    }
    local function read(data, reader)
        data['rt'] = reader.read_len_prefixed_utf16_string()
    end
    local function write(data, writer)
        writer.write_len_prefixed_utf16_string(data['rt'])
    end
    return { read, write, parameter_info }
end

local function system_font()
    local parameter_info = {
        face = { type = 8, list_items = {} }
    }
    local function read(data, reader)
        data['face'] = reader.read_len_prefixed_utf16_string()
    end
    local function write(data, writer)
        writer.write_len_prefixed_utf16_string(data['face'])
    end
    return { read, write, parameter_info }
end

local function system_size()
    local parameter_info = {
        percent = { type = 1, list_items = {} }
    }
    local function read(data, reader)
        data['percent'] = reader.read_uint16()
    end
    local function write(data, writer)
        writer.write_uint16(tonumber(data['percent']))
    end
    return { read, write, parameter_info }
end

local function system_color()
    local parameter_info = {
        r = { type = 0, list_items = {} },
        g = { type = 0, list_items = {} },
        b = { type = 0, list_items = {} },
        a = { type = 0, list_items = {} }
    }
    local function read(data, reader)
        data['r'] = reader.read_uint8()
        data['g'] = reader.read_uint8()
        data['b'] = reader.read_uint8()
        data['a'] = reader.read_uint8()
    end
    local function write(data, writer)
        writer.write_uint8(tonumber(data['r']))
        writer.write_uint8(tonumber(data['g']))
        writer.write_uint8(tonumber(data['b']))
        writer.write_uint8(tonumber(data['a']))
    end
    return { read, write, parameter_info }
end

local function system_pagebreak()
    local function read(data, reader)
    end
    local function write(data, writer)
    end
    return { read, write }
end

local stream_functions = {
    [0] = {
        name = "System",
        tags = {
            [0] = { name = "Ruby", stream_function = system_ruby },
            [1] = { name = "Font", stream_function = system_font },
            [2] = { name = "Size", stream_function = system_size },
            [3] = { name = "Color", stream_function = system_color },
            [4] = { name = "Pagebreak", stream_function = system_pagebreak },
        }
    }
}

return stream_functions
