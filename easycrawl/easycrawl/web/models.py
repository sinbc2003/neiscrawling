"""
데이터베이스 모델
크롤러 히스토리, 실행 기록, 설정 등을 저장
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum
import os

Base = declarative_base()


class CrawlerStatus(enum.Enum):
    """크롤러 실행 상태"""
    DRAFT = "draft"           # 생성됨, 아직 실행 안함
    RUNNING = "running"       # 실행 중
    PAUSED = "paused"         # 일시정지
    COMPLETED = "completed"   # 완료
    FAILED = "failed"         # 실패
    CANCELLED = "cancelled"   # 취소됨


class Crawler(Base):
    """크롤러 정보"""
    __tablename__ = 'crawlers'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # 크롤러 사양 (JSON)
    spec = Column(JSON, nullable=False)

    # 설정
    output_format = Column(String(10), default='jsonl')  # json, jsonl, csv
    request_delay = Column(Integer, default=500)  # 밀리초

    # 파일 경로
    code_file_path = Column(String(500))
    output_file_path = Column(String(500))

    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 태그 (검색용)
    tags = Column(String(500))  # 쉼표로 구분

    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'spec': self.spec,
            'output_format': self.output_format,
            'request_delay': self.request_delay,
            'code_file_path': self.code_file_path,
            'output_file_path': self.output_file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'tags': self.tags.split(',') if self.tags else []
        }


class CrawlerRun(Base):
    """크롤러 실행 기록"""
    __tablename__ = 'crawler_runs'

    id = Column(Integer, primary_key=True)
    crawler_id = Column(Integer, nullable=False)

    # 실행 상태
    status = Column(Enum(CrawlerStatus), default=CrawlerStatus.DRAFT)

    # 진행 상황
    total_items = Column(Integer, default=0)
    collected_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)

    # 체크포인트 정보
    checkpoint = Column(JSON)  # {page: 10, offset: 100}

    # 이어서 수집을 위한 정보
    last_collected_id = Column(String(255))  # 마지막 수집한 항목 ID
    last_collected_date = Column(String(50))  # 마지막 수집한 항목 날짜
    collection_mode = Column(String(50), default='from_scratch')  # from_scratch, fresh_start, incremental

    # 프로세스 정보
    pid = Column(Integer)  # 실행 중인 프로세스 ID

    # 로그
    log_file_path = Column(String(500))
    error_message = Column(Text)

    # 시간
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    paused_at = Column(DateTime)

    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'crawler_id': self.crawler_id,
            'status': self.status.value if self.status else None,
            'total_items': self.total_items,
            'collected_items': self.collected_items,
            'failed_items': self.failed_items,
            'progress': round((self.collected_items / self.total_items * 100), 2) if self.total_items else 0,
            'checkpoint': self.checkpoint,
            'last_collected_id': self.last_collected_id,
            'last_collected_date': self.last_collected_date,
            'collection_mode': self.collection_mode,
            'pid': self.pid,
            'log_file_path': self.log_file_path,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'paused_at': self.paused_at.isoformat() if self.paused_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Settings(Base):
    """전역 설정"""
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 데이터베이스 초기화
def init_db(db_path='easycrawl.db'):
    """데이터베이스 초기화"""
    db_url = f'sqlite:///{db_path}'
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def get_db_session(db_path='easycrawl.db'):
    """DB 세션 가져오기"""
    db_url = f'sqlite:///{db_path}'
    engine = create_engine(db_url, echo=False)
    Session = sessionmaker(bind=engine)
    return Session()
