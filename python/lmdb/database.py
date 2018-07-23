import os
import shutil
import random
import lmdb
from collections.abc import MutableMapping
import struct
import cbor2
import pickle
import datetime

# https://github.com/google/flatbuffers/blob/master/docs/source/CppUsage.md#access-of-untrusted-buffers

class PersistentMap(MutableMapping):
    """
    Abstract base class for persistent maps stored in LMDB.
    """

    def __init__(self, *args, **kwargs):
        self._slot = kwargs.pop('slot', 0)
        self._indexes = {}

    def attach_transaction(self, txn):
        #print('LMDB transaction attached', dir(txn))
        self._txn = txn

    def attach_index(self, index_name, index_key, index_map):
        self._indexes[index_name] = (index_key, index_map)

    def truncate(self, rebuild_indexes=True):
        #print('TRUNCATE on map')
        key_from = struct.pack('<H', self._slot)
        key_to = struct.pack('<H', self._slot + 1)
        cursor = self._txn._txn.cursor()
        cnt = 0
        if cursor.set_range(key_from):
            key = cursor.key()
            while key < key_to:
                if not cursor.delete(dupdata=True):
                    break
                cnt += 1
                self._txn._dels += 1
                self._txn._log.append((BaseTransaction.DEL, key))
        if rebuild_indexes:
            deleted, _ = self.rebuild_indexes()
            cnt += deleted
        return cnt

    def rebuild_indexes(self):
        total_deleted = 0
        total_inserted = 0
        for index_name in sorted(self._indexes.keys()):
            deleted, inserted = self.rebuild_index(index_name)
            total_deleted += deleted
            total_inserted += inserted
            print('rebuilt index "{}": {} deleted, {} inserted'.format(index_name, deleted, inserted))
        return total_deleted, total_inserted

    def rebuild_index(self, index_name):
        if index_name in self._indexes:
            index_key, index_map = self._indexes[index_name]

            deleted = index_map.truncate()

            key_from = struct.pack('<H', self._slot)
            key_to = struct.pack('<H', self._slot + 1)
            cursor = self._txn._txn.cursor()
            inserted = 0
            if cursor.set_range(key_from):
                while cursor.key() < key_to:
                    data = cursor.value()
                    if data:
                        value = self._deserialize_value(data)

                        _key = struct.pack('<H', index_map._slot) + index_map._serialize_key(index_key(value))
                        _data = index_map._serialize_value(value.oid)

                        self._txn.put(_key, _data)
                        inserted += 1
                    if not cursor.next():
                        break
            return deleted, inserted
        else:
            raise Exception('no index "{}" attached'.format(index_name))

    def _serialize_key(self, key):
        raise Exception('not implemented')

    def _serialize_value(self, value):
        raise Exception('not implemented')

    def _deserialize_value(self, data):
        raise Exception('not implemented')

    def __getitem__(self, key):
        _key = struct.pack('<H', self._slot) + self._serialize_key(key)
        _data = self._txn.get(_key)
        if _data:
            return self._deserialize_value(_data)
        else:
            return None

    def __setitem__(self, key, value):
        _key = struct.pack('<H', self._slot) + self._serialize_key(key)
        _data = self._serialize_value(value)
        self._txn.put(_key, _data)

        for index_key, index_map in self._indexes.values():
            _key = struct.pack('<H', index_map._slot) + index_map._serialize_key(index_key(value))
            _data = index_map._serialize_value(key)
            self._txn.put(_key, _data)

    def __delitem__(self, key):
        _key = struct.pack('<H', self._slot) + self._serialize_key(key)
        self._txn.delete(_key)

    def __iter__(self):
        raise Exception('not implemented')

    def __len__(self):
        raise Exception('not implemented')


class MapStringOid(PersistentMap):
    """
    Persistent map with string (utf8) keys and OID (uint64) values.

    This is used eg for string->OID indexes.
    """

    def _serialize_key(self, key):
        return key.encode('utf8')

    def _serialize_value(self, value):
        return struct.pack('<Q', value)

    def _deserialize_value(self, data):
        return struct.unpack('<Q', data)[0]


class MapOidCbor(PersistentMap):
    """
    Persistent map with OID (uint64) keys and CBOR values.

    This is used eg for transparent storage of dynamically typed data
    in object tables in a language neutral, flexible and binary transparent
    format.
    """

    def _serialize_key(self, key):
        return struct.pack('<Q', key)

    def _serialize_value(self, value):
        return cbor2.dumps(value)

    def _deserialize_value(self, data):
        return cbor2.loads(data)


class MapOidPickle(PersistentMap):
    """
    Persistent map with OID (uint64) keys and Python pickle values.

    This is used eg for transparent storage of native Python object tables.
    """

    def _serialize_key(self, key):
        return struct.pack('<Q', key)

    def _serialize_value(self, value):
        return pickle.dumps(value, protocol=4)

    def _deserialize_value(self, data):
        return pickle.loads(data)


class BaseTransaction(object):

    PUT = 1
    DEL = 2

    def __init__(self, env, write=False):
        self._env = env
        self._write = write
        self._txn = None
        self._log = []
        self._puts = 0
        self._dels = 0

    def get(self, key):
        return self._txn.get(key)

    def put(self, key, data):
        self._puts += 1
        self._log.append((BaseTransaction.PUT, key))
        return self._txn.put(key, data)

    def delete(self, key):
        self._dels += 1
        self._log.append((BaseTransaction.DEL, key))
        return self._txn.delete(key)

    def attach(self):
        raise Exception('not implemented')

    def __enter__(self):
        assert(self._txn is None)
        self._txn = lmdb.Transaction(self._env, write=self._write)
        self.attach()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        assert(self._txn is not None)
        # https://docs.python.org/3/reference/datamodel.html#object.__exit__
        # If the context was exited without an exception, all three arguments will be None.
        if exc_type is None:
            cnt = 0
            for op, key in self._log:
                _key = struct.pack('<H', 0)
                _data = struct.pack('<H', op) + key
                self._txn.put(_key, _data)
                cnt += 1
            self._txn.commit()
            print('LMDB transaction committed: {} logs records, {} puts, {} deletes'.format(cnt, self._puts, self._dels))
        else:
            self._txn.abort()
            print('LMDB transaction aborted', exc_type, exc_value, traceback)
