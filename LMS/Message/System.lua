local function system_ruby()
    local function read(data, reader)
        data['rt'] = reader.read_len_prefixed_utf16_string()
    end
    local function write(data, writer)
        writer.write_len_prefixed_utf16_string(data['rt'])
    end
    return { read, write }
end

local function system_font()
    local function read(data, reader)
        data['face'] = reader.read_len_prefixed_utf16_string()
    end
    local function write(data, writer)
        writer.write_len_prefixed_utf16_string(data['face'])
    end
    return { read, write }
end

local function system_size()
    local function read(data, reader)
        data['percent'] = reader.read_uint16()
    end
    local function write(data, writer)
        writer.write_uint16(tonumber(data['percent']))
    end
    return { read, write }
end

local function system_color()
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
    return { read, write }
end

local function system_pagebreak()
    local function read(data, reader)
    end
    local function write(data, writer)
    end
    return { read, write }
end

local stream_functions = {
    ["system_ruby"] = system_ruby,
    ["system_font"] = system_font,
    ["system_size"] = system_size,
    ["system_color"] = system_color,
    ["system_pagebreak"] = system_pagebreak
}

return stream_functions
