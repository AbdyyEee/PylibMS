from LMS.Common.LMS_Block import LMS_Block
from LMS.Stream.Reader import Reader
from LMS.Stream.Writer import Writer


class LMS_HashTable:
    """A class that represents a generic hash table block.
    
    https://github.com/kinnay/Nintendo-File-Formats/wiki/LMS-File-Format#hash-tables"""
    def __init__(self):
        self.block = LMS_Block()
        self.labels: dict[int:str] = {}
    
    def get_index_by_label(self, label: str) -> None:
        """Returns the index of a label given its name

        :param `label`: The label to find the index of."""
        for index in self.labels:
            if self.labels[index] == label:
                return index
 
    def add_label(self, label: str) -> None:
        """Adds a label to the hash tabel block.

        param `label`: The label to add."""
        for index in self.labels:
            if self.labels[index] == label:
                raise Exception("This label is already in the block.")

        index = len(self.labels)
        self.labels[index] = label

    def delete_label(self, label: str) -> None:
        """Deletes a label in the hash table block

        :param `label`: The label to delete."""
        new = {}
        found = False
        for index in self.labels:
            if self.labels[index] == label:
                found = True

        if not found:
            raise Exception("This label does not exist in the block.")

        index = self.get_index_by_label(label)
        # Add all the labels before index
        for i in range(index):
            new[i] = self.labels[i]
        # Add all the labels after index
        for i in range(index + 1, len(self.labels)):
            new[i - 1] = self.labels[i]


    def edit_label(self, label: str, new_labeL: str) -> None:
        """Edits a label in the hash table block.

        :param `label`: The existing label to edit.
        :param `new_label`: The new label.
        """
        index = self.get_index_by_label(label)
        self.labels[index] = new_labeL

    def read(self, reader: Reader) -> None:
        """Reads the hash table block from a stream.

        :param `reader`: A Reader object."""
        self.block.read_header(reader)
        slot_count = reader.read_uint32()

        for _ in range(slot_count):
            label_count = reader.read_uint32()
            offset = reader.read_uint32()
            end = reader.tell()
            reader.seek(self.block.data_start)
            reader.seek(offset, 1)

            for _ in range(label_count):
                length = reader.read_uint8()
                label = reader.read_string_len(length)
                item_index = reader.read_uint32()
                self.labels[item_index] = label

            reader.seek(end)
        
        sorted_labels = {}
       
        for index in sorted(self.labels):
            sorted_labels[index] = self.labels[index]

        self.labels = sorted_labels

    def calc_hash(self, label, num_slots) -> int:
        """Returns the hash of a label.

        :param `label`: The label.
        :param `num_slots`: The amount of hash table slots.

        https://github.com/kinnay/Nintendo-File-Formats/wiki/LMS-File-Format#hash-tables"""
        hash = 0
        for char in label:
            hash = hash * 0x492 + ord(char)
        return (hash & 0xFFFFFFFF) % num_slots

    def write(self, writer: Writer, slot_count: int) -> None:
        """Writes the hash table block to a stream.

        :param `writer`: A Writer object.
        :param `slot_count`: The hash table slot count. 101 for MSBT, 29 for MSBP and 59 for MSBF."""
        self.block.write_header(writer)
        self.block.data_start = writer.tell()
        writer.write_uint32(slot_count)

        hash_slots = {}
        # Add each label to each hash slot
        for index in self.labels:
            label = self.labels[index]
            hash = self.calc_hash(label, slot_count)
            if hash not in hash_slots:
                hash_slots[hash] = [label]
            else:
                 hash_slots[hash].append(label)
        size = 0
        label_offsets = slot_count * 8 + 4
        size += label_offsets

        hash_slots = dict(
            sorted(hash_slots.items(), key=lambda x: x[0]))

        # Write the slots
        for i in range(slot_count):
            if i in hash_slots:
                writer.write_uint32(len(hash_slots[i]))
                writer.write_uint32(label_offsets)

                for label in hash_slots[i]:
                    label_offsets += len(label) + 5
            else:
                writer.write_uint32(0)
                writer.write_uint32(label_offsets)

        # Write the labels
        for key in hash_slots:
            labels = hash_slots[key]
            for label in labels:
                label_index = self.get_index_by_label(label)
                writer.write_uint8(len(label))
                writer.write_string(label)
                writer.write_uint32(label_index)
                size += 5 + len(label)

        self.block.size = size
        self.block.write_end_data(writer)
