/**
 * @author See Contributors.txt for code contributors and overview of BadgerDB.
 *
 * @section LICENSE
 * Copyright (c) 2012 Database Group, Computer Sciences Department, University of Wisconsin-Madison.
 */

#include <memory>
#include <iostream>
#include "buffer.h"
#include "file_iterator.h"
#include "exceptions/buffer_exceeded_exception.h"
#include "exceptions/page_not_pinned_exception.h"
#include "exceptions/page_pinned_exception.h"
#include "exceptions/bad_buffer_exception.h"
#include "exceptions/hash_not_found_exception.h"

namespace badgerdb { 

BufMgr::BufMgr(std::uint32_t bufs)
  : numBufs(bufs) {
  bufDescTable = new BufDesc[bufs];

  for (FrameId i = 0; i < bufs; i++) 
  {
    bufDescTable[i].frameNo = i;
    bufDescTable[i].valid = false;
  }

  bufPool = new Page[bufs];

  int htsize = ((((int) (bufs * 1.2))*2)/2)+1;
  hashTable = new BufHashTbl (htsize);  // allocate the buffer hash table

  clockHand = bufs - 1;
}


BufMgr::~BufMgr() {
  for(int i = 0;i < numBufs;++ i){
    BufDesc *desc = &bufDescTable[i];

    if(desc->valid){
      if(desc->dirty){
        // flush page to desk
        desc->file->writePage(bufPool[i]);
      }
      // update BufDesc and hashTable
      desc->valid = false;
      hashTable->remove(desc->file, desc->pageNo);
    }
  }
  delete hashTable;
}

void BufMgr::advanceClock()
{
  // if clockHand reaches the end of buf, set it to the begin
  clockHand = clockHand + 1 == numBufs ? 0 : clockHand + 1;
}


void BufMgr::allocBuf(FrameId & frame) 
{

  // length of the current pinned flame sequence
  uint32_t totPinCnt = 0;
  while(totPinCnt < numBufs){
    advanceClock();
    BufDesc *desc = &bufDescTable[clockHand];
    if(desc->valid && desc->pinCnt > 0){
      totPinCnt ++;
    } else {
      totPinCnt = 0;
    }

    if(desc->valid){
      if(desc->refbit){
        desc->refbit = false;
        continue;
      }
      if(desc->pinCnt > 0){
        continue;
      }
      if(desc->dirty){
        // flush page to desk
        desc->file->writePage(bufPool[clockHand]);
      }
      // update BufDesc and hashTable
      desc->valid = false;
      hashTable->remove(desc->file, desc->pageNo);
    }
    // clear description of this frame
    frame = clockHand;
    return;
  }
  // buffer full, throw exception
  throw BufferExceededException();
}

  
void BufMgr::readPage(File* file, const PageId pageNo, Page*& page)
{
  try
  {
    FrameId frame;
    hashTable->lookup(file, pageNo, frame);
    // case 2: page is in the buffer pool
    BufDesc *desc = &bufDescTable[frame];
    desc->refbit = true;
    desc->pinCnt ++;
    page = &bufPool[frame];
  }
  catch(HashNotFoundException e)
  {
    // case 1: page is not in the buffer pool
    FrameId frame;
    // allocate a frame for this page
    allocBuf(frame);
    // read from memory
    bufPool[frame] = file->readPage(pageNo);

    // update BufDesc and hashTable
    BufDesc *desc = &bufDescTable[frame];
    desc->Set(file, pageNo);
    hashTable->insert(file, pageNo, frame);
    page = &bufPool[frame];
  }
}

void BufMgr::unPinPage(File* file, const PageId pageNo, const bool dirty) 
{
  try
  {
    FrameId frame;
    hashTable->lookup(file, pageNo, frame);
    // get the description of the frame
    BufDesc *desc = &bufDescTable[frame];
    if(dirty){
      desc->dirty = true;
    }
    if(desc->pinCnt > 0){
      desc->pinCnt --;
    } else {
      // pinCnt = 0, throw exception
      throw PageNotPinnedException(file->filename(), pageNo, frame);
    }
  }
  catch(HashNotFoundException e)
  {
    // do nothing
  }
}

void BufMgr::flushFile(const File* file) 
{
  for (FileIterator iter = file->begin();
      iter != file->end();
      ++iter) {
    PageId pageNo = iter.page_number();

    try
    {
      FrameId frame;
      hashTable->lookup(file, pageNo, frame);
      // get the description of the frame
      BufDesc *desc = &bufDescTable[frame];
      if(desc->pinCnt > 0){
        throw PagePinnedException(file->filename(), pageNo, frame);
      }
      if(!desc->valid || desc->file != file){
        throw BadBufferException(frame, desc->dirty, desc->valid, desc->refbit);
      }
      if(desc->dirty){
        file->writePage(bufPool[frame]);
      }
      hashTable->remove(file, pageNo);
      desc->Clear();
    }
    catch(HashNotFoundException e)
    {
      // do nothing
    }
  }
}

void BufMgr::allocPage(File* file, PageId &pageNo, Page*& page) 
{
    FrameId frame;

    // allocate an empty page in the specified file
    Page newPage = file->allocatePage();
    pageNo = newPage.page_number();

    // allocate a frame for this page
    allocBuf(frame);
    bufPool[frame] = newPage;
    page = &bufPool[frame];

    // update BufDesc and hashTable
    BufDesc *desc = &bufDescTable[frame];
    desc->Set(file, pageNo);
    hashTable->insert(file, pageNo, frame);
}

void BufMgr::disposePage(File* file, const PageId pageNo)
{
  try
  {
    FrameId frame;
    hashTable->lookup(file, pageNo, frame);

    // update BufDesc and hashTable
    BufDesc *desc = &bufDescTable[frame];
    desc->valid = false;
    hashTable->remove(file, pageNo);
  }
  catch(HashNotFoundException e)
  {
    // do nothing
  }
}

void BufMgr::printSelf(void) 
{
  BufDesc* tmpbuf;
  int validFrames = 0;
  
  for (std::uint32_t i = 0; i < numBufs; i++)
  {
    tmpbuf = &(bufDescTable[i]);
    std::cout << "FrameNo:" << i << " ";
    tmpbuf->Print();

    if (tmpbuf->valid == true)
      validFrames++;
  }

  std::cout << "Total Number of Valid Frames:" << validFrames << "\n";
}

}
