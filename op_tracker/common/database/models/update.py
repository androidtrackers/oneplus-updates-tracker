"""OnePlus Updates Tracker Database Update model"""
from typing import Union

from sqlalchemy import Column, Integer, String

from op_tracker.common.database.models import Base


class Update(Base):
    """
    Update class that represents a device update
    """

    __tablename__ = "updates"
    id: int = Column(Integer, primary_key=True)
    device: str = Column(String)
    region: str = Column(String)
    version: str = Column(String)
    branch: str = Column(String)
    type: str = Column(String)
    size: str = Column(String)
    md5: str = Column(String)
    filename: str = Column(String)
    link: str = Column(String)
    date: str = Column(String)
    changelog: str = Column(String)
    changelog_link: Union[str, None] = Column(String)
    insert_date: str = Column(String)
    product: str = Column(String)

    def __repr__(self):
        return "<User(device='%s', version='%s', branch='%s')>" % (
            self.device,
            self.version,
            self.branch,
        )
